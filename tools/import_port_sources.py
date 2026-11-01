from pathlib import Path
import json
import shutil
import sys

SOURCE_COMMIT = '58bf1d2b6ec336cc6547507f525ad0c89e7326f1'
root = Path.cwd()
upstream = Path(sys.argv[1]).resolve()
marker = root / 'PORT_SOURCE.json'
if marker.exists():
    if json.loads(marker.read_text())['commit'] != SOURCE_COMMIT:
        raise SystemExit('Unexpected source marker; refusing to overwrite sources')
    raise SystemExit(0)

for name in ('src', 'fabric'):
    if (root / name).exists():
        raise SystemExit(f'{name} already exists without provenance; refusing overwrite')

shutil.copytree(upstream / 'src', root / 'src')
shutil.copytree(upstream / 'fabric' / 'src', root / 'fabric' / 'src')

updates = {
    'minecraft_version': '26.3',
    'supported_versions': '26.3',
    'fabric_loader_version': '0.19.5',
    'fabric_api_version': '0.160.7+26.3',
    'fabric_mc_version_range': '~26.3',
    'fabric_modmenu_version': '21.0.0',
    'mod_source': 'https://github.com/Sheep-Shap/Nostalgic-Tweaks',
    'mod_issues': 'https://github.com/Sheep-Shap/Nostalgic-Tweaks/issues',
}
lines = []
for line in (upstream / 'gradle.properties').read_text(encoding='utf-8-sig').splitlines():
    key = line.split('=', 1)[0]
    if key.startswith('neoforge_') or line.strip() == '# NeoForge':
        continue
    lines.append(f'{key}={updates[key]}' if key in updates else line)
(root / 'gradle.properties').write_text('\n'.join(lines) + '\n')

metadata = root / 'fabric/src/main/resources/fabric.mod.json'
data = json.loads(metadata.read_text(encoding='utf-8-sig'))
data['depends']['fabricloader'] = '>=0.19.5'
data['depends']['java'] = '>=25'
metadata.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

marker.write_text(json.dumps({
    'repository': 'Nostalgica-Reverie/Nostalgic-Tweaks',
    'branch': '26.1.x',
    'commit': SOURCE_COMMIT,
    'target': 'Minecraft Java 26.3, Fabric only',
    'status': 'Initial migration candidate; Java API and mixin compatibility unverified'
}, indent=2) + '\n')
(root / '.gitignore').write_text('.gradle/\nbuild/\nrun/\n.idea/\n*.iml\n')
