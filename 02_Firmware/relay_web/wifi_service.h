#pragma once
#include <Arduino.h>
namespace WifiService {
void begin();
void update(uint32_t now);
const String& apName();
}
