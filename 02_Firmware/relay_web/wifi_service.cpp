#include "wifi_service.h"
#include "config.h"
#include <Preferences.h>
#include <WiFi.h>
namespace {
String name;
uint32_t attemptedAt = 0;
void migrateProfile() {
  Preferences prefs;
  if (!prefs.begin("relay-net", false)) {
    Serial.println("NVS unavailable; using compiled LAB profile");
    return;
  }
  // Only this project's Wi-Fi keys; never clear NVS or unrelated secrets.
  const char* keys[] = {"ssid", "password", "ap_password"};
  const char* values[] = {Config::StaSsid, Config::StaPassword, Config::ApPassword};
  for (size_t i = 0; i < 3; ++i)
    if (prefs.getString(keys[i], "") != values[i]) prefs.putString(keys[i], values[i]);
  prefs.end();
}
}
void WifiService::begin() {
  migrateProfile();
  WiFi.persistent(false);
  WiFi.mode(WIFI_AP_STA);
  WiFi.setAutoReconnect(true);
  char suffix[7];
  snprintf(suffix, sizeof(suffix), "%06llX", ESP.getEfuseMac() & 0xffffffULL);
  name = String("JIN-Relay-") + suffix;
  if (!WiFi.softAP(name.c_str(), Config::ApPassword)) Serial.println("Recovery AP failed");
  WiFi.begin(Config::StaSsid, Config::StaPassword); // Explicitly overrides SDK's old STA profile.
  attemptedAt = millis();
  Serial.printf("STA: %s; recovery AP: %s, IP: %s\n", Config::StaSsid, name.c_str(), WiFi.softAPIP().toString().c_str());
}
void WifiService::update(uint32_t now) {
  static bool wasConnected = false;
  const bool connected = WiFi.status() == WL_CONNECTED;
  if (connected && !wasConnected) Serial.printf("STA connected: %s\n", WiFi.localIP().toString().c_str());
  wasConnected = connected;
  if (!connected && uint32_t(now - attemptedAt) >= Config::ReconnectMs) {
    attemptedAt = now;
    WiFi.reconnect();
  }
}
const String& WifiService::apName() { return name; }
