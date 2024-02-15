#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

#define flashLED 4 // Flash LED
#define canalPWM 2 // available PWM chan 

bool ledState = false;

const char *WIFI_SSID = "GalaxyA53";
const char *WIFI_PASS = "dkue5838";

WebServer server(80);

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(640, 480);
static auto hiRes = esp32cam::Resolution::find(1280, 720);
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

void serveLED(int duty)
{
  ledcWrite(canalPWM, duty);
  String msg = duty == 0 ? "LED OFF" : "LED ON";
  Serial.println(msg);
  server.send(200, "text/plain", msg);
}

void ledStatus(){
  server.send(200, "text/plain", ledState ? "LED is ON" : "LED is OFF");
}

void ledOn(){
  ledState = true;
  serveLED(10);
}

void ledOff(){
  ledState = false;
  serveLED(0);
}

void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes))
  {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes))
  {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void handleJpgMid()
{
  if (!esp32cam::Camera.changeResolution(midRes))
  {
    Serial.println("SET-MID-RES FAIL");
  }
  serveJpg();
}

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
  // pinMode(flashLED, OUTPUT);
  ledcSetup(canalPWM, 5000, 8);
  ledcAttachPin(flashLED, canalPWM);
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /lo.jpg");
  Serial.println("  /hi.jpg");
  Serial.println("  /mid.jpg");

  server.on("/lo.jpg", handleJpgLo);
  server.on("/hi.jpg", handleJpgHi);
  server.on("/mid.jpg", handleJpgMid);
  server.on("/led", ledStatus);
  server.on("/led/on", ledOn);
  server.on("/led/off", ledOff);

  server.begin();
}

void loop()
{
  server.handleClient();
}