#include "app.h"
#include "firmware_version.h"
#include "watchdog.h"
#include "relay_driver.h"
#include "wifi_service.h"
#include "web_server.h"
namespace { RelayDriver relays; }
void App::begin() {
  // Start external watchdog before NVS, I2C, Wi-Fi and HTTP startup.
  const bool watchdogStarted = Watchdog::begin();
  Serial.begin(115200);
  Serial.printf("JIN Relay v%s | Build UTC %s\n", FW_VERSION, FW_BUILD_UTC);
  Serial.println(FW_BUILD_ID);
  if (!watchdogStarted) {
    Serial.println("FATAL: watchdog task creation failed; relays left untouched");
    for (;;) vTaskDelay(pdMS_TO_TICKS(1000));
  }
  Serial.println("External watchdog: GPIO2, HIGH 2ms / period 25ms (scheduler nominal)");
  if (!relays.begin()) Serial.println(relays.error());
  WifiService::begin();
  Web::begin(relays);
}
void App::update() {
  const uint32_t now = millis();
  relays.update(now);
  WifiService::update(now);
  Web::update();
}
