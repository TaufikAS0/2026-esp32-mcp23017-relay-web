# JIN ESP32 MCP23017 Relay Web

Simple open-source local web controller for eight ULN2803-driven relays.
Initial firmware **v0.1.0**. Target: classic ESP32 Dev Module / Arduino-ESP32 **3.3.10**.
The fitted module/flash size and wiring still require bench confirmation. This is not the Compact QC firmware.

## Wiring

| Signal | Connection |
|---|---|
| I2C SDA / SCL | ESP32 GPIO21 / GPIO22 (Compact reference) |
| MCP23017 address | `0x20`, BANK=0; dedicated port B |
| Relay 1–8 | GPB0–GPB7 -> ULN2803 inputs 1B–8B |
| ULN2803 COM / GND | +5V coil supply / common GND, per supplied mapping |
| External watchdog DONE | **ESP32 GPIO2**, separate from MCP |

ULN2803 sinks coil current: HIGH input means ON, assuming coils wired to +5V.
MCP23017 logic and I2C pull-ups must be ESP32-compatible (3.3V); COM=5V does not specify the MCP supply.
Use suitable input pulldowns / reset circuitry if outputs must remain OFF while the MCU/MCP is resetting.
Software cannot guarantee OFF before initialization or after I2C/driver failure.

**Do not flash this on an unchanged Compact board:** its source maps TPL DONE to MCP1B7,
while this requested board maps B7 to relay 8 and DONE to GPIO2. Check wiring first.
GPIO2 is a classic ESP32 boot strap; external circuitry must not prevent boot/download.

## Connect and control

Public lab profile is embedded **intentionally, with the owner's permission**:
STA SSID `HuaweiJIN`, password `jayaabadi100`.
Recovery AP `JIN-Relay-<device suffix>`, password `12345678`, normally `http://192.168.4.1`.
AP remains available while STA reconnects. Serial (115200) prints the actual STA/AP IP.
Open the device's IP in a browser. UI assets are embedded; no CDN/internet required.

Control is unauthenticated on the LAN/AP. A public GitHub repository makes the source accessible;
it does **not** expose the physical device to the internet. Internet access still depends on routing/firewall.
No OTA in this initial scope; USB upload only.

Relays initialize OFF and retain their commanded state until another command or reboot.
Closing a browser or losing Wi-Fi does not automatically turn them OFF. Commands use explicit state,
so retries do not toggle unexpectedly. Status is MCP latch readback, not contact/load feedback.
On I2C failure, OFF is attempted, status becomes UNKNOWN, and controls lock until repair/reboot.
No automatic re-arm after a bus fault. Port A is untouched; dedicate this MCP port B to relays.

Watchdog task starts before I2C/NVS/Wi-Fi: nominal HIGH 2ms, period 25ms at GPIO2,
adapted from Compact's 25ms / HIGH >=1ms timing. Task scheduling can add jitter.
It continues during web requests, reconnects and MCP faults. This independent feed does not certify
application health: a stuck web loop may coexist with a running watchdog task.
Pulse waveform, timeout compatibility, and actual reset behavior require bench measurement.

## API

| Method | Path | Form fields |
|---|---|---|
| GET | `/api/status` | none |
| POST | `/api/relay` | `channel=1..8`, `state=0` or `1` |
| POST | `/api/all` | `state=0` or `1` |

```sh
curl http://DEVICE_IP/api/status
curl -X POST http://DEVICE_IP/api/relay -d 'channel=1&state=1'
curl -X POST http://DEVICE_IP/api/all -d 'state=0'
```

Bad inputs return 400; MCP faults return 503. GET never changes outputs.
`mask` is null when hardware state cannot be trusted. `buildUTC` is build time, not device clock/uptime.

## Build / upload

Install Python 3.11+, Arduino CLI and the pinned ESP32 core:

```sh
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32@3.3.10 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
python scripts/build.py --cli arduino-cli
python -m unittest discover -s tests -v
node tests/ui.cjs
```

Windows: `./Build-Firmware.ps1` discovers the Arduino IDE CLI automatically.
Build wrapper generates fresh UTC identity + nonce, performs a clean compile, verifies binary identity,
and writes `build/manifest.json` with version, UTC, board/core and application SHA-256.
Missing metadata fails compilation; stale/mismatched binary fails the gate. Use this wrapper for every build.
Direct IDE compilation is not the verified build path. CI uploads binary + manifest artifacts.

After checking actual board, flash size, GPIO2 and COM port, upload the generated build:

```sh
arduino-cli upload --fqbn esp32:esp32:esp32 --port YOUR_PORT --input-dir build 02_Firmware/relay_web
```

Default ESP32 Dev Module flash/partition profile is used (4MB); do not assume Compact's 16MB layout.
Uploading can replace another application/partition layout. No device upload has been performed for this project.

## NVS and architecture

Only `relay-net` keys `ssid`, `password`, `ap_password` are migrated when their values differ.
Compiled lab credentials override any old SDK STA profile on every boot using `WiFi.begin`.
No NVS erase, calibration migration, or modification of other application namespaces.
Old namespaces may remain on a reused device but are not consumed by this application.
Relay state is deliberately not persisted. Files separate config, MCP driver, network, watchdog, web UI and App.

See [validation and rules](04_Dokumen/VALIDATION.md) and [changelog](CHANGELOG.md).
Development follows `develop -> feature/* -> PR -> develop`; production releases use `release/* -> main`.
For the initial public preview, GitHub opens `feature/relay-web-control`; the implementation PR targets `develop`.
After review/merge, maintainers should set the default branch back to `develop`.
MIT license. Public lab credentials do not grant permission to publish unrelated private credentials.
