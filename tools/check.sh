#!/usr/bin/env bash
# tools/check.sh — Repository validation gate
set -euo pipefail

echo "==> Validating YAML registries..."
python3 -c "
import yaml, glob
for path in glob.glob('schemas/registry/*.yaml'):
    with open(path) as f:
        yaml.safe_load(f)
    print(f'  ✓ {path}')
"

echo "==> Checking external spec pins..."
python3 -c "
import yaml, hashlib
with open('external-specs/okf/PIN.yaml') as f:
    pin = yaml.safe_load(f)
with open('external-specs/okf/SPEC.md', 'rb') as f:
    h_spec = hashlib.sha256(f.read()).hexdigest()
assert h_spec == pin['retrieved']['sha256'], f'SPEC.md hash mismatch: {h_spec} vs {pin[\"retrieved\"][\"sha256\"]}'
with open('external-specs/okf/LICENSE.md', 'rb') as f:
    h_lic = hashlib.sha256(f.read()).hexdigest()
assert h_lic == pin['license']['sha256'], f'LICENSE.md hash mismatch: {h_lic} vs {pin[\"license\"][\"sha256\"]}'
print('  ✓ OKF PIN.yaml matches SPEC.md and LICENSE.md')
"

echo "==> Checking cross-registry consistency..."
python3 -c "
import yaml
with open('schemas/registry/object_registry.yaml') as f:
    obj_types = set(yaml.safe_load(f)['object_types'].keys())
with open('schemas/registry/relation_registry.yaml') as f:
    rel_data = yaml.safe_load(f)['relations']
for rel, data in rel_data.items():
    for st in data['source_types']:
        assert st in obj_types, f'{rel} invalid source_type {st}'
    for tt in data['target_types']:
        assert tt in obj_types, f'{rel} invalid target_type {tt}'
print('  ✓ Cross-registry source_types/target_types conform')
"

echo "==> Checking canonical fixtures..."
python3 -c "
import glob, yaml
fixtures = glob.glob('fixtures/canonical/**/*.md', recursive=True)
assert len(fixtures) >= 20, f'Expected >= 20 fixtures, found {len(fixtures)}'
for p in fixtures:
    with open(p) as f:
        content = f.read()
    parts = content.split('---')
    assert len(parts) >= 3, f'{p} missing frontmatter fence'
    fm = yaml.safe_load(parts[1])
    assert 'id' in fm and 'title' in fm and 'object_type' in fm
print(f'  ✓ {len(fixtures)} canonical fixtures parsed and frontmatter-verified')
"

echo "==> Gate passed successfully."
