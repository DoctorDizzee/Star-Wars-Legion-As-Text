import json
import glob
import pathlib
import re

base = pathlib.Path('.')
unit_paths = sorted(base.glob('data/units/**/*.json'))

# Load points master
points_master = json.loads((base / 'data' / 'points_master.json').read_text(encoding='utf-8'))


def slug(name):
    slug_value = name.lower()
    slug_value = slug_value.replace("'", "")
    slug_value = slug_value.replace('/', '_')
    slug_value = re.sub(r"[^a-z0-9]+", '_', slug_value)
    return slug_value.strip('_')

FACTION_ALIAS = {
    'Galactic Empire': 'empire',
    'Galactic Republic': 'republic',
    'Rebel Alliance': 'rebel',
    'Separatist Alliance': 'separatists',
    'Mercenary': 'mercenary'
}

def faction_slug(faction):
    return FACTION_ALIAS.get(faction, slug(faction))

keyword_defs = {
    'deflect': {
        'name': 'Deflect',
        'slug': 'deflect',
        'type': 'Unit Keyword',
        'timing': 'During Attack: Defense',
        'official_rules_text': 'While a unit with the Deflect keyword is defending against a ranged attack, if it spends a dodge token, it gains "Surge: Block". Furthermore, if it spends a dodge token and the attack is ranged, the attacker suffers 1 wound for each surge result rolled by the defender during the Roll Defense Dice step.',
        'ai_processing_logic': [
            'Condition 1: Attack must be Ranged.',
            "Effect 1 (Defense): Defender's surge chart temporarily becomes Surge to Block.",
            'Effect 2 (Damage): Attacker suffers 1 wound if the defender rolls any Surge result (max 1).',
            'Exceptions: Does not trigger in melee.'
        ],
        'last_updated': '2024-04-22'
    },
    'impact': {
        'name': 'Impact',
        'slug': 'impact',
        'type': 'Weapon Keyword',
        'timing': 'During Attack: Offense',
        'official_rules_text': 'While attacking a unit that has Armor, change up to X Hit results to Critical results.',
        'ai_processing_logic': [
            'Condition 1: Target unit must have the Armor keyword.',
            'Effect: Convert standard Hits to Crits, up to the X value.',
            'Interaction Note: This happens before the defender applies the Armor keyword.'
        ],
        'last_updated': '2024-04-22'
    }
}

rules_dir = base / 'rules' / 'keywords'
rules_dir.mkdir(parents=True, exist_ok=True)


def convert_kw(kw):
    if isinstance(kw, dict):
        if 'ref' in kw:
            return kw
        if kw.get('name') is not None:
            ref = f"keywords/{slug(kw['name'])}"
            new_kw = {'ref': ref}
            if 'value' in kw:
                new_kw['value'] = kw['value']
            return new_kw
        return kw

    if isinstance(kw, str):
        ref = f"keywords/{slug(kw)}"
        return {'ref': ref}

    return kw

for p in unit_paths:
    data = json.loads(p.read_text(encoding='utf-8'))
    data['keywords'] = [convert_kw(kw) for kw in data.get('keywords', [])]
    for w in data.get('weapons', []):
        w['keywords'] = [convert_kw(kw) for kw in w.get('keywords', [])]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

keyword_slugs = set()
for p in unit_paths:
    data = json.loads(p.read_text(encoding='utf-8'))
    for kw in data.get('keywords', []):
        if isinstance(kw, dict) and 'ref' in kw:
            keyword_slugs.add(kw['ref'].split('/', 1)[1])
        elif isinstance(kw, str):
            keyword_slugs.add(slug(kw))
    for w in data.get('weapons', []):
        for kw in w.get('keywords', []):
            if isinstance(kw, dict) and 'ref' in kw:
                keyword_slugs.add(kw['ref'].split('/', 1)[1])
            elif isinstance(kw, str):
                keyword_slugs.add(slug(kw))

new_keyword_count = 0
for s in sorted(keyword_slugs):
    path = rules_dir / f'{s}.json'
    if path.exists():
        continue
    if s in keyword_defs:
        definition = keyword_defs[s]
    else:
        definition = {
            'name': s.replace('_', ' ').title(),
            'slug': s,
            'type': 'Keyword',
            'description': 'Placeholder keyword definition. Add official rules text and AI processing logic.',
            'source': 'Unit dataset cross-reference'
        }
    path.write_text(json.dumps(definition, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    new_keyword_count += 1


def get_points_for_unit(data, uid):
    points_units = points_master.get('units', {})
    if uid in points_units:
        return points_units[uid]

    faction = data.get('faction')
    name = data.get('name')
    if not faction or not name:
        return None

    stable_key = f"{faction_slug(faction)}/{slug(name)}"
    title = data.get('title')
    if title and title != 'None':
        stable_key += f"/{slug(title)}"
    if stable_key in points_units:
        return points_units[stable_key]

    unit_key = name
    if title and title != 'None':
        unit_key += f" ({title})"
    return points_units.get(unit_key)


compiled = []
for p in unit_paths:
    data = json.loads(p.read_text(encoding='utf-8'))
    uid = p.relative_to(base / 'data' / 'units').as_posix()
    points = get_points_for_unit(data, uid)
    if points is not None:
        data['points'] = points
    compiled.append({'id': uid, 'source': p.as_posix(), **data})

compiled_path = base / 'compiled' / 'all_units.json'
compiled_path.write_text(json.dumps(compiled, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

print('wrote', new_keyword_count, 'new keyword json files')
print('rewrote', len(unit_paths), 'unit json files')
print('wrote compiled file', compiled_path)
