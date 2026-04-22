import json
import glob
import pathlib
import re

base = pathlib.Path('.')
unit_paths = sorted(base.glob('data/units/**/*.json'))


def slug(name):
    slug_value = name.lower()
    slug_value = slug_value.replace("'", "")
    slug_value = slug_value.replace('/', '_')
    slug_value = re.sub(r"[^a-z0-9]+", '_', slug_value)
    return slug_value.strip('_')

keyword_names = set()
for p in unit_paths:
    data = json.loads(p.read_text(encoding='utf-8'))
    for kw in data.get('keywords', []):
        if isinstance(kw, dict) and kw.get('name') is not None:
            keyword_names.add(kw['name'])
    for w in data.get('weapons', []):
        for kw in w.get('keywords', []):
            if isinstance(kw, dict) and kw.get('name') is not None:
                keyword_names.add(kw['name'])

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

for name in sorted(keyword_names):
    s = slug(name)
    if s in keyword_defs:
        definition = keyword_defs[s]
    else:
        definition = {
            'name': name,
            'slug': s,
            'type': 'Keyword',
            'description': 'Placeholder keyword definition. Add official rules text and AI processing logic.',
            'source': 'Unit dataset cross-reference'
        }
    (rules_dir / f'{s}.json').write_text(json.dumps(definition, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def convert_kw(kw):
    if not isinstance(kw, dict) or kw.get('name') is None:
        return kw
    ref = f"keywords/{slug(kw['name'])}"
    new_kw = {'ref': ref}
    if 'value' in kw:
        new_kw['value'] = kw['value']
    return new_kw

for p in unit_paths:
    data = json.loads(p.read_text(encoding='utf-8'))
    data['keywords'] = [convert_kw(kw) for kw in data.get('keywords', [])]
    for w in data.get('weapons', []):
        w['keywords'] = [convert_kw(kw) for kw in w.get('keywords', [])]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

compiled = []
for p in unit_paths:
    data = json.loads(p.read_text(encoding='utf-8'))
    uid = p.relative_to(base / 'data' / 'units').as_posix()
    compiled.append({'id': uid, 'source': p.as_posix(), **data})

compiled_path = base / 'compiled' / 'all_units.json'
compiled_path.write_text(json.dumps(compiled, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

print('wrote', len(keyword_names), 'keyword json files')
print('rewrote', len(unit_paths), 'unit json files')
print('wrote compiled file', compiled_path)
