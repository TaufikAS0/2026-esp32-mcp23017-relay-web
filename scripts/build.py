"""Pinned, clean Arduino build with fresh identity and final binary gate."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
SKETCH = ROOT / '02_Firmware' / 'relay_web'
OUT = ROOT / 'build'
FQBN = 'esp32:esp32:esp32'
CORE = '3.3.10'

def version():
    return re.search(r'#define FW_VERSION "(\d+\.\d+\.\d+)"',
                     (SKETCH / 'firmware_version.h').read_text()).group(1)

def generate():
    OUT.mkdir(exist_ok=True)
    identity = {'version': version(), 'buildUTC': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'nonce': uuid.uuid4().hex, 'fqbn': FQBN, 'core': CORE}
    identity['marker'] = f"jin-relay|{identity['version']}|{identity['buildUTC']}|{identity['nonce']}"
    (SKETCH / 'build_metadata.h').write_text(
        '#pragma once\n' + f'#define FW_BUILD_VERSION "{identity["version"]}"\n'
        + f'#define FW_BUILD_UTC "{identity["buildUTC"]}"\n'
        + f'#define FW_BUILD_ID "{identity["marker"]}"\n', encoding='utf-8')
    (OUT / 'identity.json').write_text(json.dumps(identity, indent=2), encoding='utf-8')
    return identity

def verify(identity, binary):
    if identity['version'] != version():
        raise ValueError('Version changed after metadata generation')
    data = Path(binary).read_bytes()
    if identity['marker'].encode() not in data:
        raise ValueError('Missing or stale binary identity')
    manifest = {**identity, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                'binary': Path(binary).name}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', default=shutil.which('arduino-cli') or str(
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe'))
    args = parser.parse_args()
    cores = json.loads(subprocess.check_output([args.cli, 'core', 'list', '--format', 'json']))
    if not any(p['id'] == 'esp32:esp32' and p['installed_version'] == CORE for p in cores['platforms']):
        raise SystemExit('Install esp32:esp32@' + CORE)
    identity = generate()
    # Remove prior proof before compiling; a failed build cannot retain a valid manifest.
    (OUT / 'manifest.json').unlink(missing_ok=True)
    subprocess.run([args.cli, 'compile', '--clean', '--jobs', '4', '--fqbn', FQBN,
                    '--output-dir', str(OUT), str(SKETCH)], check=True)
    print(json.dumps(verify(identity, OUT / 'relay_web.ino.bin'), indent=2))

if __name__ == '__main__':
    main()
