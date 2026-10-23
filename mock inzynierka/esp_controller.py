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

    def send_frame(self, active_keys, next_note, upcoming_notes, wrong_keys, midi_start, num_keys, num_leds=144, active_leds=122, hint_state=0, is_repeated=0):
        if not self.ser or not self.ser.is_open:
            return

        # Klawisze wciśnięte przez użytkownika (Niebieski)
        user_indices = []
        for note in active_keys:
            mapped = int((note - midi_start) / num_keys * active_leds)
            idx = (num_leds - 1) - mapped
            if 0 <= idx < num_leds:
                user_indices.append(idx)

        # Błędy użytkownika (Czerwony)
        wrong_indices = []
        for note in wrong_keys:
            mapped = int((note - midi_start) / num_keys * active_leds)
            idx = (num_leds - 1) - mapped
            if 0 <= idx < num_leds:
                wrong_indices.append(idx)

        # Aktualna nuta do wciśnięcia (Hit / Hint ze stanem)
        hit_index = -1
        if next_note:
            h_note = next_note['note']
            mapped_h = int((h_note - midi_start) / num_keys * active_leds)
            hit_index = (num_leds - 1) - mapped_h

        # Nadchodzące nuty - Preview (Przygaszony żółty)
        preview_indices = []
        for note in upcoming_notes:
            mapped_p = int((note['note'] - midi_start) / num_keys * active_leds)
            idx = (num_leds - 1) - mapped_p
            if 0 <= idx < num_leds and idx != hit_index:
                preview_indices.append(idx)

        # Formatowanie ramki tekstowej dla ESP32
        u_str = ",".join(map(str, user_indices)) if user_indices else "-1"
        w_str = ",".join(map(str, wrong_indices)) if wrong_indices else "-1"
        
        # TUTAJ DODANO TRZECIĄ WARTOŚĆ (is_repeated): Format "indeks,stan,is_repeated"
        if hit_index != -1:
            h_str = f"{hit_index},{hint_state},{1 if is_repeated else 0}"
        else:
            h_str = "-1,0,0"

        p_str = ",".join(map(str, preview_indices)) if preview_indices else "-1"
        
        message = f"U:{u_str}|W:{w_str}|H:{h_str}|P:{p_str}\n"
        try:
            self.ser.write(message.encode("utf-8"))
        except Exception as e:
            print(f"[ESP32] Błąd wysyłania danych: {e}")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[ESP32] Zamknięto połączenie szeregowe.")