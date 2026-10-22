import time
import serial

class ESPController:
    def __init__(self, port="COM3", baudrate=115200):
        self.ser = None
        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.01)
            time.sleep(2)
            print("[ESP32] Połączono pomyślnie z taśmą LED.")
        except Exception as e:
            self.ser = None
            print(f"[ESP32] Błąd połączenia z portem szeregowym: {e}")

    def send_frame(self, active_keys, next_note, is_waiting, midi_start, num_keys, num_leds=144, active_leds=122):
        if not self.ser or not self.ser.is_open:
            return

        #Zbieramy klawisze naciśnięte przez użytkownika
        user_indices = []
        for note in active_keys:
            mapped_led = int((note - midi_start) / num_keys * active_leds)
            key_index = (num_leds - 1) - mapped_led
            if 0 <= key_index < num_leds:
                user_indices.append(key_index)

        #Sprawdzamy czy mamy podpowiedź (w trybie WAIT)
        hint_index = -1
        if next_note and is_waiting:
            h_note = next_note['note']
            mapped_hint = int((h_note - midi_start) / num_keys * active_leds)
            hint_index = (num_leds - 1) - mapped_hint

        #Formatowanie wiadomości tekstowej dla ESP
        u_str = ",".join(map(str, user_indices)) if user_indices else "-1"
        h_str = str(hint_index) if hint_index != -1 else "-1"
        
        message = f"U:{u_str}|H:{h_str}\n"
        try:
            self.ser.write(message.encode("utf-8"))
        except Exception as e:
            print(f"[ESP32] Błąd wysyłania danych: {e}")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[ESP32] Zamknięto połączenie szeregowe.")
