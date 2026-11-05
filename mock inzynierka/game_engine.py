import time
from learning_tool import LearningTool

class GameEngine:
    def __init__(self, song_notes):
        self.song_notes = song_notes
        self.score = 0
        self.game_mode = "WAIT"  # "WAIT" lub "FLOW"
        self.song_virtual_time = 0.0
        self.active_keys = set()
        self.feedback_text = ""
        self.feedback_timer = 0.0
        
        # Słownik błędów {note_id: expire_timestamp}
        self.wrong_keys_timers = {}

        # Inicjalizacja modułu odpowiedzialnego stricte za podpowiedzi i edukację
        self.learning_tool = LearningTool(preview_window=1.2)

    def update(self, dt, events):
        next_note = next((n for n in self.song_notes if not n['hit']), None)

        # Logika WAIT MODE (zatrzymanie czasu, dopóki gracz nie uderzy właściwej nuty)
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
                        next_note['hit'] = True
                        self.score += 100
                        self.set_feedback("HIT!")
                    else:
                        self.wrong_keys_timers[note] = time.time() + 0.4
                        self.set_feedback("WRONG KEY!")

            elif status == 128 or (status == 144 and velocity == 0):
                self.active_keys.discard(note)

        # Wygaszanie przedawnionych błędów (0.4s)
        current_time = time.time()
        self.wrong_keys_timers = {
            note: exp_time 
            for note, exp_time in self.wrong_keys_timers.items() 
            if exp_time > current_time
        }

        # Pobieramy gotowy zestaw podpowiedzi i stanów wizualnych z modułu edukacyjnego
        cues = self.learning_tool.get_learning_cues(
            self.song_notes, 
            self.song_virtual_time, 
            self.game_mode, 
            self.wrong_keys_timers
        )

        return cues["next_note"], cues["is_waiting"], cues["upcoming_notes"], cues["wrong_keys"]

    def set_feedback(self, text):
        self.feedback_text = text
        self.feedback_timer = time.time()

    def toggle_mode(self):
        self.game_mode = "FLOW" if self.game_mode == "WAIT" else "WAIT"