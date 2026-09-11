#!/usr/bin/env bash
# tools/check.sh — Repository validation gate
set -euo pipefail

# Anchor to the repository root regardless of invocation CWD.
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Choose python binary (prefer .venv if available)
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
    RUFF=".venv/bin/ruff"
    PYTEST=".venv/bin/pytest"
else
    PYTHON="python3"
    RUFF="ruff"
    PYTEST="pytest"
fi

echo "==> Running Ruff linter on Python code..."
$RUFF check .

echo "==> Validating YAML registries via trashheap CLI..."
$PYTHON -m trashheap.cli check-registries

echo "==> Checking external spec pins..."
$PYTHON -c "
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

echo "==> Checking canonical fixtures frontmatter..."
$PYTHON -c "
import glob, yaml
fixtures = glob.glob('fixtures/canonical/**/*.md', recursive=True)
assert len(fixtures) >= 20, f'Expected >= 20 fixtures, found {len(fixtures)}'
for p in fixtures:
    with open(p) as f:
        content = f.read()
    parts = content.split('---', 2)
    assert len(parts) >= 3, f'{p} missing frontmatter fence'
    fm = yaml.safe_load(parts[1])
    assert 'id' in fm and 'title' in fm and 'object_type' in fm
print(f'  ✓ {len(fixtures)} canonical fixtures parsed and frontmatter-verified')
"

echo "==> Checking Agent Skills drift (E050)..."
$PYTHON -m trashheap.cli generate-skills --check

echo "==> Running multi-layered linter across canonical fixtures..."
$PYTHON -m trashheap.cli lint fixtures/canonical

echo "==> Generating and verifying conformance matrix and status drift (D90, CONFORM-001)..."
$PYTHON -m trashheap.cli conformance --check

echo "==> Running pytest test suite with coverage gate (>= 70%)..."
$PYTEST -q --cov=trashheap --cov-fail-under=70

echo "==> Gate passed successfully."
