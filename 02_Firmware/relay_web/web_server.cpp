#include "web_server.h"
#include "config.h"
#include "firmware_version.h"
#include "wifi_service.h"
#include "web_ui.h"
#include <WebServer.h>
#include <WiFi.h>
namespace {
WebServer server(80);
RelayDriver* driver;
void error(int status, const char* message) {
  server.send(status, "application/json", String("{\"error\":\"") + message + "\"}");
}
void status() {
  String json = "{\"version\":\"" FW_VERSION "\",\"buildUTC\":\"" FW_BUILD_UTC "\",\"mcpAddress\":\"0x20\",\"ready\":";
  json += driver->ready() ? "true" : "false";
  json += ",\"mask\":";
  json += driver->ready() ? String(driver->mask()) : "null";
  json += ",\"error\":\"" + String(driver->error()) + "\",\"staConnected\":";
  json += WiFi.status() == WL_CONNECTED ? "true" : "false";
  json += ",\"staIP\":\"" + WiFi.localIP().toString() + "\",\"apIP\":\"" + WiFi.softAPIP().toString();
  json += "\",\"apName\":\"" + WifiService::apName() + "\",\"watchdogPin\":2,\"watchdogPeriodMs\":25,\"watchdogHighMs\":2,\"uptimeMs\":" + String(millis()) + "}";
  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "application/json", json);
}
bool validState() { return server.hasArg("state") && (server.arg("state") == "0" || server.arg("state") == "1"); }
void setRelay() {
  if (server.args() != 2 || !server.hasArg("channel") || !validState()) return error(400, "Use channel=1..8 and state=0 or 1");
  String ch = server.arg("channel");
  if (ch.length() != 1 || ch[0] < '1' || ch[0] > '8') return error(400, "Invalid channel");
  uint8_t bit = uint8_t(1U << (ch[0] - '1'));
  uint8_t next = server.arg("state") == "1" ? (driver->mask() | bit) : (driver->mask() & ~bit);
  if (!driver->setMask(next)) return error(503, "MCP fault; physical relay state unknown");
  status();
}
void setAll() {
  if (server.args() != 1 || !validState()) return error(400, "Use state=0 or 1");
  if (!driver->setMask(server.arg("state") == "1" ? 0xff : 0)) return error(503, "MCP fault; physical relay state unknown");
  status();
}
}
void Web::begin(RelayDriver& relays) {
  driver = &relays;
  server.on("/", HTTP_GET, [] { server.send_P(200, "text/html; charset=utf-8", WebUi); });
  server.on("/api/status", HTTP_GET, status);
  server.on("/api/relay", HTTP_POST, setRelay);
  server.on("/api/all", HTTP_POST, setAll);
  server.onNotFound([] { error(404, "Route or method not found"); });
  server.begin();
}
void Web::update() { server.handleClient(); }
