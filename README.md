## funkcjonalności

* **Wizualizator spadających nut:** Graficzna prezentacja utworów MIDI w czasie rzeczywistym.
* **Integracja z klawiaturą MIDI:** Obsługa urządzeń fizycznych przez interfejs `pygame.midi`.
* **Kalibracja zakresu klawiatury:** Procedura mapująca skrajny lewy i prawy klawisz instrumentu użytkownika, zapisująca konfigurację w pliku `config.json`.
* **Dwa tryby gry/nauki:**
  * **Tryb WAIT (Oczekiwanie):** Zatrzymuje przewijanie utworu do momentu, aż użytkownik wciśnie właściwą nutę.
  * **Tryb FLOW (Płynny):** Utwór leci nieprzerwanie.

---

## opis kodu

* **`main.py`**
  * Inicjalizuje środowisko graficzne Pygame.
  * Odpowiada za główną pętlę programu, obsługę skrótów klawiszowych (`[M]` – zmiana trybu, `[R]` – kalibracja) oraz renderowanie grafiki (spadające nuty, linia trafień, wirtualna klawiatura, HUD z punktacją).

* **`game_engine.py`**
  * Zawiera klasę `GameEngine` zarządzającą logiką gry, czasem wirtualnym utworu (`song_virtual_time`) oraz stanem nut (czy zostały trafione).
  * Obsługuje logikę weryfikacji trafień w trybie *FLOW* (na podstawie okna czasowego) oraz blokowanie czasu w trybie *WAIT*.
  * Odpowiada za system naliczania punktów oraz wyświetlanie komunikatów zwrotnych.

* **`midi_handler.py`**
  * Odpowiada za wykrywanie i inicjalizację podłączonego sprzętu MIDI za pomocą `pygame.midi` oraz bezpieczne zamykanie połączenia.
  * Udostępnia metodę `read_events()` pobierającą bieżące zdarzenia z klawiatury.
  * Zawiera funkcję `load_midi_notes()`, która parsuje plik `.mid` przy użyciu biblioteki `mido` i zwraca posortowaną listę słowników z informacjami o nutach (klawisz, czas startu, czas trwania).

* **`calibration.py`**
  * Odpowiada za proces wykrywania zakresu klawiszy fizycznych instrumentu użytkownika.
  * Zapisuje wykryty zakres oraz liczbę klawiszy do pliku konfiguracyjnego `config.json` (oraz odczytuje go przy ponownym uruchomieniu, pomijając kalibrację, jeśli plik istnieje).
