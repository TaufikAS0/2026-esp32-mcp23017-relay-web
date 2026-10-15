"""Upload only verified bootloader/table/factory ranges. Never write boot_app0 at 0xe000."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import build

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--esptool', required=True, help='Path to esptool v5 executable')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--backup', help='Local backup of 0..0x48ffff: boot, NVS and full factory slot')
    mode.add_argument('--erase-all', action='store_true', help='Explicitly erase all device data before upload; no backup required')
    args = parser.parse_args()
    if args.backup and Path(args.backup).stat().st_size != 0x490000:
        raise SystemExit('A complete 0x490000-byte boot/NVS/factory backup is required')
    manifest = json.loads((build.OUT / 'manifest.json').read_text())
    if manifest['fqbn'] != build.FQBN or manifest['version'] != build.version():
        raise SystemExit('Build target/version mismatch')
    data = (build.OUT / manifest['binary']).read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest['sha256'] or manifest['marker'].encode() not in data:
        raise SystemExit('Binary identity/hash mismatch')
    images = build.verify_bundle()
    if images != manifest.get('images'):
        raise SystemExit('Flash bundle hash/range mismatch')
    probe = subprocess.check_output([args.esptool, '--port', args.port, '--baud', '115200', 'flash-id'], text=True)
    print(probe)
    if 'ESP32-S3' not in probe or 'Detected flash size: 16MB' not in probe:
        raise SystemExit('Expected ESP32-S3 with 16MB flash')
    if args.erase_all:
        subprocess.run([args.esptool, '--chip', 'esp32s3', '--port', args.port,
                        '--baud', '460800', 'erase-flash'], check=True)
    command = [args.esptool, '--chip', 'esp32s3', '--port', args.port, '--baud', '460800', 'write-flash']
    for image in images.values():
        command += [hex(image['offset']), str(build.OUT / image['file'])]
    subprocess.run(command, check=True)

if __name__ == '__main__':
    main()
