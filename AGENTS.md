# Project rules

Read the workspace vault in `../2026 Vault Firmware Rules`, starting at
`00_Start_Here/Firmware_AI_Vault_Home.md`, then `01_Rules/Rules_Nama_dan_Folder_Workspace.md`,
`Rules_Firmware_Standar.md`, `Rules_GitHub_Gitflow.md`, `Rules_Kredensial_WiFi.md`,
`04_Profiles/WiFi/WiFi_HuaweiJIN.md`, `01_Rules/Rules_Versioning.md`, and
`01_Rules/Rules_Change_Notifications.md` before firmware work/build/push.
Public contributors without that private vault should use this repository's documented contracts;
lab maintainers must resolve the vault before changing connectivity policy.

- Work on feature/* from develop; reviewed PR to develop. Do not push directly to main or auto-merge.
- Dedicated MCP23017 0x20 B0..B7 are relays; watchdog is ESP32 GPIO2, NEVER MCP B7.
- The older Compact board has a different watchdog mapping. Do not copy its entire hardware profile.
- Only the explicitly approved public lab Wi-Fi profile may be published. No private source dumps/secrets.
- One version source: firmware_version.h. Build with scripts/build.py / Build-Firmware.ps1.
- Fresh generated identity, pinned core, binary verification and manifest required before push.
- Run Python metadata tests, node tests/ui.cjs and clean compile. Hardware claims require actual evidence.
- Update CHANGELOG and validation/handoff: version before/after, build UTC, API/pin/NVS changes,
  tests, actual Git branch/commit/PR, and upload state. Build UTC is not a running clock.
