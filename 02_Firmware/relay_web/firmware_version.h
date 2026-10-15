#pragma once
#define FW_VERSION "0.2.0"
#include "build_metadata.h"
#include <string_view>
static_assert(std::string_view(FW_VERSION) == FW_BUILD_VERSION,
              "Run Build-Firmware.ps1 to regenerate build identity");
