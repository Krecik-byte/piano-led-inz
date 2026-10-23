import time

class GameEngine:
    def __init__(self, song_notes):
        self.song_notes = song_notes
        self.score = 0
        self.game_mode = "WAIT"  # "WAIT" lub "FLOW"
        self.song_virtual_time = 0.0
        self.active_keys = set()
        self.feedback_text = ""
        self.feedback_timer = 0.0
        
        # Pamięć błędów - słownik {note_id: expire_timestamp}
        self.wrong_keys_timers = {}

    def update(self, dt, events):
        next_note = next((n for n in self.song_notes if not n['hit']), None)

        # Logika WAIT MODE
        is_waiting = False
        if self.game_mode == "WAIT" and next_note is not None:
            if self.song_virtual_time >= next_note['start_time']:
                is_waiting = True
                self.song_virtual_time = next_note['start_time']

        if not is_waiting:
            self.song_virtual_time += dt

        # Obsługa wejścia MIDI
        for status, note, velocity in events:
            if status == 144 and velocity > 0:
                self.active_keys.add(note)

                if self.game_mode == "FLOW":
                    hit_matched = False
                    for n in self.song_notes:
                        if not n['hit'] and n['note'] == note:
                            time_diff = abs(self.song_virtual_time - n['start_time'])
                            if time_diff < 0.15:
                                n['hit'] = True
                                self.score += 100
                                self.set_feedback("PERFECT!")
                                hit_matched = True
                                break
                            elif time_diff < 0.30:
                                n['hit'] = True
                                self.score += 50
                                self.set_feedback("GOOD")
                                hit_matched = True
                                break
                    if not hit_matched:
                        self.wrong_keys_timers[note] = time.time() + 0.4
                        self.set_feedback("MISS!")

                elif self.game_mode == "WAIT":
                    if next_note and note == next_note['note']:
                        if not next_note.get('pressed', False):
                            next_note['pressed'] = True
                            next_note['hold_start'] = time.time()
                            self.score += 100
                            self.set_feedback("HOLD...")
                    else:
                        self.wrong_keys_timers[note] = time.time() + 0.4
                        self.set_feedback("WRONG KEY!")

            elif status == 128 or (status == 144 and velocity == 0):
                self.active_keys.discard(note)
                # Nuta w trybie WAIT kończy się dopiero, gdy puścisz właściwy klawisz!
                if self.game_mode == "WAIT" and next_note and next_note.get('pressed', False):
                    if note == next_note['note']:
                        next_note['hit'] = True

        # Zabezpieczenie: jeśli ktoś trzyma klawisz w nieskończoność, zamknij nutę po 3s przetrzymania
        if self.game_mode == "WAIT" and next_note and next_note.get('pressed', False):
            elapsed = time.time() - next_note['hold_start']
            duration = next_note.get('duration', 0.5)
            if elapsed > duration + 3.0:
                next_note['hit'] = True

        # Wygaszanie przedawnionych błędów
        current_time = time.time()
        self.wrong_keys_timers = {
            note: exp_time 
            for note, exp_time in self.wrong_keys_timers.items() 
            if exp_time > current_time
        }

        # Obliczanie stanu LED dla hintu oraz wykrywanie powtórzeń (re-strike)
        hint_state = 0
        is_repeated = 0

        if next_note is not None:
            # Poprawione wykrywanie nut powtarzanych (szukamy przyszłych nut o tej samej wysokości)
            future_same = [n for n in self.song_notes if not n['hit'] and n['note'] == next_note['note'] and n != next_note]
            if future_same:
                next_same = min(future_same, key=lambda x: x['start_time'])
                if (next_same['start_time'] - next_note['start_time']) < 1.5:
                    is_repeated = 1

            if is_waiting and next_note.get('pressed', False):
                elapsed = time.time() - next_note['hold_start']
                duration = next_note.get('duration', 0.5)
                
                if elapsed < (duration * 0.5):
                    hint_state = 0  # 0% - 50%: Zielony puls
                elif elapsed < duration:
                    hint_state = 1  # 50% - 100% (Połowa): Fiolet lub jasna zieleń przy powtórkach
                elif elapsed < duration + 1.0:
                    hint_state = 2  # Koniec nuty (do 1s po czasie): Mruganie
                elif elapsed < duration + 2.0:
                    hint_state = 3  # Przetrzymanie ~1s: Fiolet+Czerwony (lub Czerwony+Zielony mrugający)
                else:
                    hint_state = 4  # Przetrzymanie >= 2s ("w chuj"): Obie czerwone pulsujące
            else:
                hint_state = 0

        upcoming_notes = []
        preview_window = 1.2
        for n in self.song_notes:
            if not n['hit']:
                time_until = n['start_time'] - self.song_virtual_time
                if 0 < time_until <= preview_window:
                    upcoming_notes.append(n)

        wrong_keys_active = set(self.wrong_keys_timers.keys())

        return next_note, is_waiting, upcoming_notes, wrong_keys_active, hint_state, is_repeated

    def set_feedback(self, text):
        self.feedback_text = text
        self.feedback_timer = time.time()

    def toggle_mode(self):
        self.game_mode = "FLOW" if self.game_mode == "WAIT" else "WAIT"