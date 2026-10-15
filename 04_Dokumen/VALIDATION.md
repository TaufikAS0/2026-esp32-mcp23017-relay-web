# Implementation and handoff — 2026-10-15

## Facts and decisions

- New repository, initial v0.1.0; no previous version or installed-device baseline known.
- User requested public open source and explicitly approved publishing HuaweiJIN / jayaabadi100.
- User mapping: MCP address 0x20, B0..B7 to ULN2803 1B..8B, COM +5V, GND common.
- User explicitly placed the external watchdog on GPIO2. This overrides the older Compact pin mapping.
- Fresh inspection of Compact reference commit e3204740101139337874eae67aae9ceb422100ec:
  classic ESP32, SDA21/SCL22, TPL DONE MCP1B7, 25ms interval / HIGH >=1ms.
  No Compact source or private documents were copied into this public repository.
- Dedicated GPIO2 task uses nominal HIGH 2ms / 25ms period to avoid web/reconnect starvation.
- HTTP control has no token; no OTA. Public repository access is separate from LAN device access.
- Selective NVS migration only in relay-net (ssid/password/ap_password); no erase/other namespaces.

## Assumptions / unknowns

- MCP23017 is inferred from the Compact reference and port naming; an ACK at 0x20 cannot identify an IC.
- Actual board/flash size, I2C wiring, watchdog IC/timeout, polarity/coil circuit and boot behavior need confirmation.
- Target is generic classic ESP32 Dev Module / default 4MB layout, not Compact's legacy 16MB partition profile.
- MCP must start in BANK=0; power-cycle/reset the expander before first use. Twin-register checks are a sanity check,
  not conclusive chip identification or proof against arbitrary register contents left by other firmware.
- ULN2803 HIGH=ON assumes conventional low-side coil wiring; hardware levels and current limits need bench review.
- Pulse timing includes scheduler jitter. Independent watchdog feed does not prove main-loop or HTTP health.
- Relay OFF during reset and after I2C loss is not guaranteed by software. No physical load/contact feedback exists.

## Checks

- Python tests exercise fresh identities, SHA manifest, missing/stale marker and version mismatch rejection.
- Node executes actual UI script in a simulated DOM/HTTP environment: channels 1..8, mask isolation,
  all ON/OFF, null/fault state, disabled controls, disconnect/reconnect and visible build identity.
- Pinned clean firmware build and binary identity gate results recorded below after completion.
- Tests do not emulate the firmware WebServer or MCP electrical bus. Real HTTP/API/NVS/relay/watchdog tests remain pending.
- No device upload performed. Do not replace an existing application before checking board/partition and port.

## Required workspace sources read for this task

Paths relative to the private workspace vault (not copied into public Git):

1. 00_Start_Here/Firmware_AI_Vault_Home.md
2. 01_Rules/Rules_Nama_dan_Folder_Workspace.md
3. 01_Rules/Rules_Firmware_Standar.md
4. 01_Rules/Rules_GitHub_Gitflow.md
5. 01_Rules/Rules_Kredensial_WiFi.md
6. 04_Profiles/WiFi/WiFi_HuaweiJIN.md
7. 01_Rules/Rules_Versioning.md (full)
8. 01_Rules/Rules_Change_Notifications.md (full)
9. 06_Decision_Flows/Flow_Planning_Firmware.md
10. 06_Decision_Flows/Flow_Konektivitas_dan_WiFi.md
11. 06_Decision_Flows/Flow_Pilih_Baseline_Program.md
12. 05_Safe_Programs/Safe_Module_Test_and_Reusable_Sketches.md
13. 05_Safe_Programs/Safe_Compact_QC_Curated_Subset.md

STA: HuaweiJIN / jayaabadi100. AP recovery password: 12345678.
Rules on version/build identity and change notification are linked from AGENTS.md.

## Hardware acceptance still required

Confirm MCU, MCP model, SDA21/SCL22, GPIO2 DONE wiring and GPIO2 boot strap.
Measure HIGH/period under simultaneous web traffic/reconnect/I2C faults; prove watchdog timeout/reset on a stopped feed.
Verify all eight unloaded relay coils, then actual loads and power-on/reset state with suitable precautions.
Exercise absent MCP, disconnect during ON, reboot, Wi-Fi loss/reconnect, AP access and selective NVS retention.
Confirm live /api/status version/build UTC agrees with serial and UI after a separately authorized upload.

## References

- [Microchip MCP23017 datasheet, BANK=0 register map](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/20001952C.pdf)

## Local build evidence

- PASS: clean compile via Arduino CLI 1.3.1, esp32:esp32@3.3.10, FQBN esp32:esp32:esp32.
- Version: new project -> v0.1.0. Build UTC: 2026-10-15T04:02:48Z (11:02:48 UTC+07:00).
- Compiler application usage: 975764 / 1310720 bytes (74%); globals 48368 / 327680 bytes (14%).
- Application binary: relay_web.ino.bin, 975920 bytes.
- SHA-256: 5935ce01f79f8d39bad38c3a6ddb3bbd028185e5ffd5f513d63f90ac37f1cfb2.
- Fresh version/UTC/nonce marker verified in final binary; build/manifest.json generated (ignored artifact).
- Five Python metadata tests PASS; Node UI simulation PASS. Firmware HTTP/API electrical behavior not tested live.
- Initial CLI 1.5.1 build was interrupted after a suspended orphan compiler. CLI 1.3.1 then exposed a namespace
  collision with the core Network object; renamed to WifiService. The final clean build above passed after the fix.
- Git flow: bootstrap develop, implementation feature/relay-web-control, open PR to develop; no merge/main release.
- Public preview default is feature/relay-web-control until the integration PR is reviewed/merged.
- No firmware uploaded. No measured watchdog waveform/reset, real Wi-Fi/NVS or physical relay-load acceptance.
