#pragma once
#include <Arduino.h>
namespace Config {
constexpr char StaSsid[] = "HuaweiJIN";
constexpr char StaPassword[] = "jayaabadi100"; // Intentionally public LAB profile.
constexpr char ApPassword[] = "12345678";
// GroundChecker pinlist: ESP32-S3 I2C GPIO8/9, DONE watchdog GPIO2.
constexpr int Sda = 8, Scl = 9, WatchdogPin = 2;
constexpr uint8_t McpAddress = 0x20;
constexpr uint32_t I2cHz = 100000, ReconnectMs = 15000, HealthCheckMs = 1000;
constexpr uint16_t I2cTimeoutMs = 20;
constexpr uint32_t WatchdogPeriodMs = 25, WatchdogHighMs = 2;
// HIGH drives ULN2803 input -> sink ON. No inversion in the MCP configuration.
constexpr bool RelayActiveHigh = true;
}
