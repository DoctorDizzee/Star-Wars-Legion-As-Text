import json
import pathlib
import re

BASE_DIR = pathlib.Path('.')
RULES_TEXT_PATH = BASE_DIR / 'rules_text.txt'
RULES_KEYWORDS_DIR = BASE_DIR / 'rules' / 'keywords'

COMMON_OCR_FIXES = {
    '/unie910': 'unit',
    '/unie915': 'unit',
    '/f_irst': 'first',
    '/T_he': 'The',
    '/f_lip': 'flip',
    '/f_lat': 'flat',
    '/f_lush': 'flush',
    '/f_lamethrower': 'flamethrower',
    'a/f_ter': 'after',
    'A/f_ter': 'After',
    'speci/f_ic': 'specific',
    'modi/f_iers': 'modifiers',
    'Recon/f_igure': 'Reconfigure',
    'minumum': 'minimum',
    'LEGION RULEBOOK': '',
}


def slug(name: str) -> str:
    slug_value = name.lower()
    slug_value = slug_value.replace("'", "")
    slug_value = slug_value.replace('/', ' ')
    slug_value = re.sub(r'[^a-z0-9]+', '_', slug_value)
    return slug_value.strip('_')


def clean_text(text: str) -> str:
    text = text.replace('\r\n', '\n')
    text = re.sub(r'^\d+(?=[A-Z])', '', text, flags=re.MULTILINE)
    for bad, good in COMMON_OCR_FIXES.items():
        text = text.replace(bad, good)
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('ﬀ', 'ff')
    text = text.replace('\ufb00', 'ff').replace('\ufb01', 'fi').replace('\ufb02', 'fl')
    return text


def combine_broken_headings(lines):
    combined = []
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            if (
                (line.endswith(':') or line.endswith('/') or line.endswith('-') or line.endswith('UNIT NAME') or line.endswith('FRONT/REAR/') or line.endswith('BATTLE'))
                and re.match(r'^[A-Z0-9 :/()\-]+$', next_line)
                and len(next_line.split()) <= 5
            ):
                combined.append((line + ' ' + next_line).strip())
                skip_next = True
                continue
        combined.append(line)
    return combined


def is_heading(line: str) -> bool:
    if line in {'KEYWORD', 'ACTION'}:
        return False
    return bool(re.match(r'^[A-Z0-9 :/()\-]+$', line) and len(line) > 3)


def normalize_slug(title: str) -> str:
    title = title.strip()
    if title.endswith(' X'):
        title = title[:-2].strip()
    if title.startswith('IMMUNE: '):
        return 'immune'
    if title.startswith('HOVER: '):
        return 'hover'
    if title.startswith('GUARDIAN '):
        return 'guardian'
    if title.startswith('MASTER OF THE FORCE'):
        return 'master_of_the_force'
    if title.startswith('ENRAGE '):
        return 'enrage'
    if title.startswith('JUMP '):
        return 'jump'
    if title.startswith('PRECISE '):
        return 'precise'
    if title.startswith('RECHARGE '):
        return 'recharge'
    if title.startswith('SCOUTING PARTY '):
        return 'scouting_party'
    if title.startswith('SELF-DESTRUCT '):
        return 'self_destruct'
    if title.startswith('STRATEGIZE '):
        return 'strategize'
    if title.startswith('TAKE COVER '):
        return 'take_cover'
    if title.startswith('MASTER STORYTELLER'):
        return 'master_storyteller'
    return slug(title)


def humanize_title(title: str) -> str:
    parts = title.split()
    return ' '.join(part.capitalize() if part not in {'X', 'I', 'II', 'III', 'IV'} else part for part in parts)


IGNORED_HEADINGS = {
    'COMMAND CARD KEYWORDS',
    'LEGACY TOKENS',
    'LINE OF SIGHT SILHOUETTE TEMPLATES',
    'MY MOOD IS BASED ON',
}


def parse_keywords(text: str) -> dict:
    text = clean_text(text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lines = combine_broken_headings(lines)
    keywords = {}
    current_keyword = None
    current_description = []

    for line in lines:
        if is_heading(line):
            if current_keyword:
                if current_keyword not in IGNORED_HEADINGS:
                    keywords[current_keyword] = ' '.join(current_description).strip()
            current_keyword = line.rstrip(':').strip()
            current_description = []
        elif current_keyword:
            current_description.append(line)

    if current_keyword and current_keyword not in IGNORED_HEADINGS:
        keywords[current_keyword] = ' '.join(current_description).strip()

    return keywords


def guess_type(description: str) -> str:
    desc = description.lower()
    if 'weapon keyword' in desc:
        return 'Weapon Keyword'
    if 'unit keyword' in desc:
        return 'Unit Keyword'
    return 'Keyword'


def write_keyword_defs(keywords: dict):
    RULES_KEYWORDS_DIR.mkdir(parents=True, exist_ok=True)
    for title, description in keywords.items():
        if not description:
            continue
        slug_name = normalize_slug(title)
        path = RULES_KEYWORDS_DIR / f'{slug_name}.json'
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
        else:
            data = {
                'name': humanize_title(title),
                'slug': slug_name,
                'type': guess_type(description),
                'source': 'Rulebook PDF',
            }
        if not data.get('official_rules_text') or data.get('official_rules_text', '').startswith('Placeholder'):
            data['official_rules_text'] = description
        if not data.get('description') or data.get('description', '').startswith('Placeholder'):
            data['description'] = description
        if 'type' not in data or not data['type']:
            data['type'] = guess_type(description)
        if 'source' not in data or data['source'] == 'Unit dataset cross-reference':
            data['source'] = 'Rulebook PDF'
        data['name'] = data.get('name', humanize_title(title))
        if 'slug' not in data:
            data['slug'] = slug_name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    if RULES_TEXT_PATH.exists():
        text = RULES_TEXT_PATH.read_text(encoding='utf-8')
    else:
        raise FileNotFoundError(f'{RULES_TEXT_PATH} not found')
    keywords = parse_keywords(text)
    write_keyword_defs(keywords)
    print(f'Generated {len(keywords)} keyword definitions in {RULES_KEYWORDS_DIR}')


if __name__ == '__main__':
    main()
