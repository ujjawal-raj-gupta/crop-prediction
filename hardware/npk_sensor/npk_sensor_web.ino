/*
 * NPK Modbus sensor — web bridge mode for Smart Crop Advisor
 *
 * Wiring (MAX485 / RS485 module):
 *   RO  -> Arduino pin 10 (RX)
 *   DI  -> Arduino pin 11 (TX)
 *   DE+RE -> Arduino pin 3
 *   VCC/GND -> 5V and GND (sensor often needs separate 12V per your module docs)
 *
 * Serial monitor / USB: 9600 baud
 *
 * Outputs lines the website can parse:
 *   NPK_JSON:{"n":45.2,"p":18.1,"k":39.0,"unit":"mg/kg"}
 *
 * Commands from PC (optional):
 *   READ  — take one Modbus reading immediately
 */

#include <Arduino.h>
#include <SoftwareSerial.h>

SoftwareSerial modbusSerial(10, 11);
const int DE_RE_PIN = 3;

const byte npkRequestFrame[] = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x03, 0x65, 0xCD};
byte responseBuffer[11];

const float c_N = 0.0f;
const float m_N = 1.0f;
const float c_P = -30.0f;
const float m_P = 1.0f;
const float c_K = -22.0f;
const float m_K = 1.0f;

unsigned long lastAutoReadMs = 0;
const unsigned long AUTO_READ_INTERVAL_MS = 5000;

void emitNpkJson(float n, float p, float k) {
  Serial.print(F("NPK_JSON:{\"n\":"));
  Serial.print(n, 1);
  Serial.print(F(",\"p\":"));
  Serial.print(p, 1);
  Serial.print(F(",\"k\":"));
  Serial.print(k, 1);
  Serial.println(F(",\"unit\":\"mg/kg\"}"));
}

bool readNpkSensor(float &outN, float &outP, float &outK) {
  while (modbusSerial.available() > 0) {
    modbusSerial.read();
  }

  digitalWrite(DE_RE_PIN, HIGH);
  delay(5);
  modbusSerial.write(npkRequestFrame, sizeof(npkRequestFrame));
  modbusSerial.flush();
  digitalWrite(DE_RE_PIN, LOW);

  unsigned long startTime = millis();
  while (modbusSerial.available() < 11 && (millis() - startTime < 300)) {
    delay(1);
  }

  if (modbusSerial.available() < 11) {
    Serial.println(F("NPK_ERROR:TIMEOUT"));
    return false;
  }

  for (int i = 0; i < 11; i++) {
    responseBuffer[i] = modbusSerial.read();
  }

  if (responseBuffer[0] != 0x01 || responseBuffer[1] != 0x03) {
    Serial.println(F("NPK_ERROR:FRAME"));
    return false;
  }

  uint16_t raw_N = (responseBuffer[3] << 8) | responseBuffer[4];
  uint16_t raw_P = (responseBuffer[5] << 8) | responseBuffer[6];
  uint16_t raw_K = (responseBuffer[7] << 8) | responseBuffer[8];

  outN = max(0.0f, (raw_N * m_N) + c_N);
  outP = max(0.0f, (raw_P * m_P) + c_P);
  outK = max(0.0f, (raw_K * m_K) + c_K);
  return true;
}

void setup() {
  Serial.begin(9600);
  pinMode(DE_RE_PIN, OUTPUT);
  digitalWrite(DE_RE_PIN, LOW);
  modbusSerial.begin(4800);

  Serial.println(F("NPK_READY:web-bridge"));
  Serial.println(F("Send READ or wait for auto readings every 5s."));
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();
    if (cmd == "READ") {
      float n, p, k;
      if (readNpkSensor(n, p, k)) {
        emitNpkJson(n, p, k);
      }
    }
    while (Serial.available() > 0) {
      Serial.read();
    }
  }

  if (millis() - lastAutoReadMs >= AUTO_READ_INTERVAL_MS) {
    lastAutoReadMs = millis();
    float n, p, k;
    if (readNpkSensor(n, p, k)) {
      emitNpkJson(n, p, k);
    }
  }
}
