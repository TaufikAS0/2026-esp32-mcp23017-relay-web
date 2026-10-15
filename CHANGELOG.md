# Changelog

## v0.1.0 — 2026-10-15

New project; no previous firmware version in this repository.
- Eight active-HIGH ULN2803 relay inputs on MCP23017 0x20 GPB0..GPB7; all OFF initialization.
- Local web UI, explicit relay/all commands, register health checks and fault lock.
- GPIO2 external watchdog task, nominal HIGH 2ms / 25ms period; separate from Compact MCP1B7.
- HuaweiJIN STA + persistent recovery AP with password 12345678; selective relay-net NVS updates.
- Single version header, generated UTC/nonce identity, clean pinned build and SHA-256 manifest.
- No OTA, device upload, or physical relay/watchdog acceptance in this initial implementation.
