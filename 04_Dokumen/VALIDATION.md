# Implementation and handoff — 2026-10-15

Current installed firmware is v0.2.0 on ESP32-S3; see the final section below.
The initial v0.1.0 sections are retained as historical evidence and do not describe the current target.

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

## v0.2.0 — COM10 identification, full erase and live verification

### Confirmed target and changes

- User requested USB upload and web verification, then explicitly requested a full erase.
- esptool identified ESP32-S3 revision 0.2, 16MB quad flash and 8MB octal PSRAM.
- The old application was an ESP-IDF GroundChecker image booting factory at 0x90000.
- The supplied Google Sheets GroundChecker pinlist confirms SDA GPIO8, SCL GPIO9, DONE WT GPIO2,
  MCP 0x20, and ULN2803 relay channels on B0..B7. No unrelated sheet contents were published.
- Repository firmware version 0.1.0 -> 0.2.0 (minor: corrected target/hardware support).
- FQBN: esp32:esp32:esp32s3:FlashSize=16M,FlashMode=dio,PSRAM=opi,PartitionScheme=custom.
- Added exact partition-table/bundle gates and guarded upload. Seven Python tests and Node UI simulation PASS.

### Flash procedure / data handling

- Local backup of 0x000000..0x48ffff completed before erase: bootloader, original partition table, NVS,
  otadata/phy and full old factory slot. It is not a full 16MB device backup.
- Raw backups/logs are ignored under build/ and must not be published.
- User-authorized full-chip erase PASS (38.7 seconds). All old NVS, calibration, OTA images and storage were erased.
  Earlier preservation planning no longer describes this actual deployment.
- The custom map retains the original region boundaries, reserves legacy_nvs, and uses new nvs at 0xf90000.
  On this fully erased device the reserved legacy_nvs region is empty; no old data was migrated.
- Uploaded bootloader at 0, table at 0x8000 and factory application at 0x90000; all three write hashes verified.
- No direct Arduino boot_app0/merged upload was used. Subsequent uploads use scripts/upload.py.
- Live profile: STA HuaweiJIN; recovery AP password 12345678. Application relay-net Wi-Fi keys are initialized
  in the new NVS and updated only when changed. Separate AP client authentication was not bench-tested.

### Installed build / runtime checks

- Clean Arduino-ESP32 3.3.10 build PASS; installed v0.2.0 build UTC 2026-10-15T04:18:27Z
  (11:18:27 UTC+07:00), not the device's current clock.
- Application binary 964560 bytes, SHA-256 6f1af7ce6ac76d4b804395ac8a1486a492ce770dddb5ee009856e1a8834070d3.
- Compiler application payload 964407 bytes, globals 47688 bytes. The compiler reports the whole 16MB flash
  as its custom-profile maximum; the independent artifact gate enforces the actual 4MB factory slot.
- Serial boot, live /api/status and rendered dashboard show the same version and build UTC.
- STA connection PASS; root HTML HTTP 200; /api/status ready=true, mask=0, no MCP fault.
- Browser relay 1 ON then OFF PASS in the UI/register state. All eight channel OFF commands and all-OFF API PASS.
- Seven malformed POST cases return 400; two invalid GET routes return 404; no output change.
- Twenty status samples showed no fault/reset. Normal reboot then reconnect PASS; final dashboard shows all OFF.
- Watchdog task startup confirmed in serial: GPIO2, nominal HIGH 2ms / 25ms period. This is software evidence,
  not a measured waveform, timeout/reset proof, or endurance acceptance.
- Boot prints "No core dump partition found" because this minimal map has no crash-dump partition;
  the application continues normally. No runtime crash was observed in these checks.
- Physical relay contacts/load behavior, watchdog waveform and forced-failure reset remain unmeasured.
- COM port/network identifiers, raw serial logs, screenshots and device backups remain local in ignored build/.
