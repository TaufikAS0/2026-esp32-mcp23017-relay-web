#include "watchdog.h"
#include "config.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
namespace {
void pulseTask(void*) {
  TickType_t wake = xTaskGetTickCount();
  const TickType_t highTicks = max<TickType_t>(1, pdMS_TO_TICKS(Config::WatchdogHighMs));
  const TickType_t periodTicks = max<TickType_t>(highTicks + 1, pdMS_TO_TICKS(Config::WatchdogPeriodMs));
  for (;;) {
    digitalWrite(Config::WatchdogPin, HIGH);
    vTaskDelay(highTicks);
    digitalWrite(Config::WatchdogPin, LOW);
    vTaskDelayUntil(&wake, periodTicks);
  }
}
}
bool Watchdog::begin() {
  digitalWrite(Config::WatchdogPin, LOW);
  pinMode(Config::WatchdogPin, OUTPUT);
  return xTaskCreate(pulseTask, "external-wdt", 2048, nullptr, 3, nullptr) == pdPASS;
}
