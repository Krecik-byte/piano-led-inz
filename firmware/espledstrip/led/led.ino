#include <FastLED.h>

#define NUM_LEDS 144      // Całkowita liczba diod na taśmie
#define DATA_PIN 16       // Pin sygnałowy DIN

CRGB leds[NUM_LEDS];
String inputStr = "";     // Bufor na odebrany komunikat

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(40); // Bezpieczna jasność
  FastLED.clear();
  FastLED.show();
}

void parseAndDraw(String data) {
  FastLED.clear();

  // Oczekiwany format: "U:10,12|H:45" lub "U:-1|H:45" itp.
  int hPos = data.indexOf("|H:");
  if (hPos == -1) return;

  String userPart = data.substring(2, hPos); // po "U:" do "|H:"
  String hintPart = data.substring(hPos + 3);   // po "|H:"

  // Rysujemy podpowiedź (Kolor Żółty)
  int hintIdx = hintPart.toInt();
  if (hintIdx >= 0 && hintIdx < NUM_LEDS) {
    leds[hintIdx] = CRGB(255, 180, 0); // Żółty
    if (hintIdx > 0) {
      leds[hintIdx - 1] = CRGB(255, 180, 0);
    }
  }

  // Rysujemy wciśnięte klawisze (Kolor Niebieski)
  if (userPart != "-1" && userPart.length() > 0) {
    int startIndex = 0;
    int commaIndex = userPart.indexOf(',');

    while (commaIndex != -1) {
      String token = userPart.substring(startIndex, commaIndex);
      int ledIdx = token.toInt();
      if (ledIdx >= 0 && ledIdx < NUM_LEDS) {
        leds[ledIdx] = CRGB(0, 200, 255); // Niebieski
        if (ledIdx > 0) {
          leds[ledIdx - 1] = CRGB(0, 200, 255);
        }
      }
      startIndex = commaIndex + 1;
      commaIndex = userPart.indexOf(',', startIndex);
    }

    String lastToken = userPart.substring(startIndex);
    int ledIdx = lastToken.toInt();
    if (ledIdx >= 0 && ledIdx < NUM_LEDS) {
      leds[ledIdx] = CRGB(0, 200, 255);
      if (ledIdx > 0) {
        leds[ledIdx - 1] = CRGB(0, 200, 255);
      }
    }
  }
}

void loop() {
  if (Serial.available() > 0) {
    inputStr = Serial.readStringUntil('\n');
    inputStr.trim();
    if (inputStr.length() > 0) {
      parseAndDraw(inputStr);
    }
  }

  FastLED.show();
  delay(10); 
}