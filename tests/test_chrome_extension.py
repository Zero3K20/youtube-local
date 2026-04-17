import json
from pathlib import Path


def test_chrome_extension_manifest_and_rules_are_valid():
    extension_dir = Path('chrome-extension')
    manifest = json.loads((extension_dir / 'manifest.json').read_text())
    rules = json.loads((extension_dir / 'rules.json').read_text())

    assert manifest['manifest_version'] == 3
    assert manifest['declarative_net_request']['rule_resources'][0]['path'] == 'rules.json'
    assert rules[0]['action']['type'] == 'redirect'
    assert 'youtube\\.com' in rules[0]['condition']['regexFilter']
