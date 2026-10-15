# Changelog

## v0.2.0 — 2026-10-15

- COM10 probe found ESP32-S3 / 16MB flash / 8MB octal PSRAM, rather than the provisional classic ESP32 target.
- Corrected I2C to SDA8/SCL9 from the user-provided GroundChecker pinlist. Relay B0..B7 and watchdog GPIO2 unchanged.
- Custom 16MB layout preserves original NVS as reserved legacy_nvs and allocates new nvs in unused flash tail.
- Guarded upload writes only bootloader/table/factory image, protecting legacy NVS from generic boot_app0 writes.
- Build gates now verify partition layout and all flash image hashes/offsets. Seven metadata/layout tests pass.
- USB/web verification results are recorded in 04_Dokumen/VALIDATION.md after execution.

## v0.1.0 — 2026-10-15

New project; no previous firmware version in this repository.
- Eight active-HIGH ULN2803 relay inputs on MCP23017 0x20 GPB0..GPB7; all OFF initialization.
- Local web UI, explicit relay/all commands, register health checks and fault lock.
- GPIO2 external watchdog task, nominal HIGH 2ms / 25ms period; separate from Compact MCP1B7.
- HuaweiJIN STA + persistent recovery AP with password 12345678; selective relay-net NVS updates.
- Single version header, generated UTC/nonce identity, clean pinned build and SHA-256 manifest.
- No OTA, device upload, or physical relay/watchdog acceptance in this initial implementation.
