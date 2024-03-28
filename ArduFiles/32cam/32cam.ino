#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

#define flashLED 4 // Flash LED
#define canalPWM 2 // available PWM chan 

#define RELAY 13 // Relay PIN

const char *WIFI_SSID = "SSID"; // SSID
const char *WIFI_PASS = "PASSWORD"; // PASSWORD

WebServer server(80); // Initiate web server

// Define resolutions sizes
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(640, 480);
static auto hiRes = esp32cam::Resolution::find(1280, 720);

// Capture and Send func
void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr)
  {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

// LED func
void serveLED(int duty)
{
  ledcWrite(canalPWM, duty);
  String msg = duty == 0 ? "LED OFF" : "LED ON";
  Serial.println(msg);
  server.send(200, "text/plain", msg);
}

// Electromagnet func
void serveELEC(int mode){
  String msg = mode == 0 ? "R OFF" : "R ON";
  Serial.println(msg);
  server.send(200, "text/plain", msg);
}

// LED ON handler
void ledOn(){
  serveLED(10);
}

// LED OFF handler
void ledOff(){
  serveLED(0);
}

// Electromagnet ON handler
void electroOn(){
  digitalWrite(RELAY, HIGH);
  serveELEC(1);
}

// Electromagnet OFF handler
void electroOff(){
  digitalWrite(RELAY, LOW);
  serveELEC(0);
}

// LOW RES handler
void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes))
  {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

// HIGH RES handler
void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes))
  {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

// MEDIUM RES handler
void handleJpgMid()
{
  if (!esp32cam::Camera.changeResolution(midRes))
  {
    Serial.println("SET-MID-RES FAIL");
  }
  serveJpg();
}

// Setup. Called once
void setup()
{
  Serial.begin(115200);
  Serial.println();
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }
  pinMode(RELAY, OUTPUT);
  digitalWrite(RELAY, LOW);
  ledcSetup(canalPWM, 5000, 8);
  ledcAttachPin(flashLED, canalPWM);
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }

  // Defining the http entries
  server.on("/lo.jpg", handleJpgLo);
  server.on("/hi.jpg", handleJpgHi);
  server.on("/mid.jpg", handleJpgMid);
  server.on("/led/on", ledOn);
  server.on("/led/off", ledOff);
  server.on("/electro/on", electroOn);
  server.on("/electro/off", electroOff);
  server.begin();

  // Print URLs
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /lo.jpg");
  Serial.println("  /hi.jpg");
  Serial.println("  /mid.jpg");
  Serial.println("  /led/on");
  Serial.println("  /led/off");
  Serial.println("  /electro/on");
  Serial.println("  /electro/off");
}

// Await connections
void loop()
{
  server.handleClient();
}