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

// Pomocnicza funkcja do parsowania rozdzielonych przecinkami indeksów LED
void parseAndSetLEDs(String part, CRGB color) {
  if (part == "-1" || part.length() == 0) return;

  int startIndex = 0;
  int commaIndex = part.indexOf(',');

  while (commaIndex != -1) {
    String token = part.substring(startIndex, commaIndex);
    int ledIdx = token.toInt();
    if (ledIdx >= 0 && ledIdx < NUM_LEDS) {
      leds[ledIdx] = color;
      if (ledIdx > 0) leds[ledIdx - 1] = color; // Ewentualne pogrubienie na 2 diody dla szerokości klawisza
    }
    startIndex = commaIndex + 1;
    commaIndex = part.indexOf(',', startIndex);
  }

  String lastToken = part.substring(startIndex);
  int ledIdx = lastToken.toInt();
  if (ledIdx >= 0 && ledIdx < NUM_LEDS) {
    leds[ledIdx] = color;
    if (ledIdx > 0) leds[ledIdx - 1] = color;
  }
}

void parseAndDraw(String data) {
  FastLED.clear();

  // Oczekiwany format: "U:10,12|W:15|H:45|P:50,52"
  int wPos = data.indexOf("|W:");
  int hPos = data.indexOf("|H:");
  int pPos = data.indexOf("|P:");

  if (wPos == -1 || hPos == -1 || pPos == -1) return;

  String userPart  = data.substring(2, wPos);         // Od "U:" do "|W:"
  String wrongPart = data.substring(wPos + 3, hPos);  // Od "|W:" do "|H:"
  String hintPart  = data.substring(hPos + 3, pPos);  // Od "|H:" do "|P:"
  String prevPart  = data.substring(pPos + 3);        // Od "|P:" do końca

  // 1. Nadchodzące nuty - Preview (Przygaszony pomarańczowy)
  parseAndSetLEDs(prevPart, CRGB(80, 40, 0));

  // 2. Klawisze wciśnięte przez użytkownika (Niebieski)
  parseAndSetLEDs(userPart, CRGB(0, 200, 255));

  // 3. Aktualna nuta do wciśnięcia - Hint (Pulsujący żółty)
  // Rysowany PO użytkowniku, dzięki czemu jeśli trzymasz klawisz, pulsowanie wymusza ponowne uderzenie!
  int hintIdx = hintPart.toInt();
  if (hintIdx >= 0 && hintIdx < NUM_LEDS) {
    int pulse = beatsin8(180, 20, 255); // Zwiększona częstotliwość dla wyraźniejszego mrugania
    CRGB hintColor = CRGB(255, 180, 0);
    hintColor.nscale8_video(pulse);
    
    leds[hintIdx] = hintColor;
    if (hintIdx > 0) leds[hintIdx - 1] = hintColor;
  }

  // 4. Błędy użytkownika (Czerwony) - RYSOWANE NA SAMYM KOŃCU (najwyższy priorytet)
  parseAndSetLEDs(wrongPart, CRGB(255, 0, 0));
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