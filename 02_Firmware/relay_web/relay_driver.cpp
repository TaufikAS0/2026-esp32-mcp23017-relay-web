#include "relay_driver.h"
#include "config.h"
#include <Wire.h>
namespace {
constexpr uint8_t IodirB = 0x01, IoconA = 0x0a, IoconB = 0x0b, OlatB = 0x15;
}
bool RelayDriver::read(uint8_t reg, uint8_t& value) {
  Wire.beginTransmission(Config::McpAddress);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(Config::McpAddress, uint8_t(1)) != 1) return false;
  value = Wire.read();
  return true;
}
bool RelayDriver::write(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(Config::McpAddress);
  Wire.write(reg);
  Wire.write(value);
  return Wire.endTransmission() == 0;
}
uint8_t RelayDriver::physical(uint8_t mask) const {
  return Config::RelayActiveHigh ? mask : uint8_t(~mask);
}
bool RelayDriver::fail(const char* reason, bool attemptOff) {
  // Best effort OFF, never report physical OFF as guaranteed after a bus fault.
  if (attemptOff) write(OlatB, physical(0));
  ready_ = false;
  error_ = reason;
  Serial.printf("MCP fault: %s; relay state UNKNOWN. Reboot after repair.\n", reason);
  return false;
}
bool RelayDriver::begin() {
  ready_ = false;
  Wire.begin(Config::Sda, Config::Scl, Config::I2cHz);
  Wire.setTimeOut(Config::I2cTimeoutMs);
  uint8_t a, b, value;
  // Require reset BANK=0. Do not normalize an unknown/shared register layout.
  if (!read(IoconA, a) || !read(IoconB, b) || a != b || (a & 0x81)) {
    error_ = "MCP unavailable or BANK=0 not established; outputs untouched";
    return false;
  }
  // Load OFF latch before enabling outputs; GPA is never modified.
  if (!write(OlatB, physical(0)) || !write(IodirB, 0x00) ||
      !read(IodirB, value) || value != 0 ||
      !read(OlatB, value) || value != physical(0)) return fail("Initialization failed");
  mask_ = 0;
  ready_ = true;
  error_ = "";
  return true;
}
bool RelayDriver::setMask(uint8_t mask) {
  if (!ready_) return false;
  uint8_t value;
  if (!write(OlatB, physical(mask)) || !read(OlatB, value) || value != physical(mask))
    return fail("Output write/readback failed");
  mask_ = mask;
  return true;
}
void RelayDriver::update(uint32_t now) {
  if (!ready_ || uint32_t(now - checkedAt_) < Config::HealthCheckMs) return;
  checkedAt_ = now;
  uint8_t direction, latch, a, b;
  if (!read(IoconA, a) || !read(IoconB, b) || a != b || (a & 0x81)) {
    fail("Register layout unavailable", false); // Never write using an unknown BANK map.
    return;
  }
  if (!read(IodirB, direction) || direction != 0 ||
      !read(OlatB, latch) || latch != physical(mask_)) fail("Periodic register check failed");
}
