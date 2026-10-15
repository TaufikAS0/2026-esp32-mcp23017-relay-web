#pragma once
#include <Arduino.h>
class RelayDriver {
public:
  bool begin();
  bool setMask(uint8_t mask);
  void update(uint32_t now);
  bool ready() const { return ready_; }
  uint8_t mask() const { return mask_; }
  const char* error() const { return error_; }
private:
  bool read(uint8_t reg, uint8_t& value);
  bool write(uint8_t reg, uint8_t value);
  bool fail(const char* reason, bool attemptOff = true);
  uint8_t physical(uint8_t mask) const;
  bool ready_ = false;
  uint8_t mask_ = 0;
  uint32_t checkedAt_ = 0;
  const char* error_ = "Not initialized";
};
