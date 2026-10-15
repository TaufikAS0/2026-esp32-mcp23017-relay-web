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
import struct

ROOT = Path(__file__).resolve().parents[1]
SKETCH = ROOT / '02_Firmware' / 'relay_web'
OUT = ROOT / 'build'
FQBN = 'esp32:esp32:esp32s3:FlashSize=16M,FlashMode=dio,PSRAM=opi,PartitionScheme=custom'
CORE = '3.3.10'

EXPECTED_PARTITIONS = [
    (1, 0x40, 0x9000, 0x80000, 'legacy_nvs'),
    (1, 0, 0x89000, 0x2000, 'otadata'),
    (1, 1, 0x8b000, 0x1000, 'phy_init'),
    (0, 0, 0x90000, 0x400000, 'factory'),
    (0, 0x10, 0x490000, 0x400000, 'ota_0'),
    (0, 0x11, 0x890000, 0x400000, 'ota_1'),
    (1, 0x82, 0xc90000, 0x2f7000, 'storage'),
    (1, 2, 0xf90000, 0x60000, 'nvs'),
]

def verify_partitions(data):
    entries = []
    for offset in range(0, len(data) - 31, 32):
        magic, kind, subtype, address, size, label, flags = struct.unpack('<HBBII16sI', data[offset:offset + 32])
        if magic != 0x50aa:
            break
        entries.append((kind, subtype, address, size, label.split(b'\0')[0].decode()))
        if flags:
            raise ValueError('Unexpected partition flags')
    if entries != EXPECTED_PARTITIONS:
        raise ValueError('Partition map mismatch: legacy NVS must remain reserved')
    return entries

def verify_bundle():
    verify_partitions((OUT / 'relay_web.ino.partitions.bin').read_bytes())
    images = {'bootloader': ('relay_web.ino.bootloader.bin', 0),
              'partitions': ('relay_web.ino.partitions.bin', 0x8000),
              'application': ('relay_web.ino.bin', 0x90000)}
    result = {}
    for role, (name, offset) in images.items():
        data = (OUT / name).read_bytes()
        limit = {'bootloader': 0x8000, 'partitions': 0x1000, 'application': 0x400000}[role]
        if not data or len(data) > limit:
            raise ValueError('Image exceeds allowed write range: ' + role)
        result[role] = {'file': name, 'offset': offset, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return result

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
    images = verify_bundle()
    manifest = verify(identity, OUT / 'relay_web.ino.bin')
    manifest['images'] = images
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
