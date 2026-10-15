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
                    for n in self.song_notes:
                        if not n['hit'] and n['note'] == note:
                            time_diff = abs(self.song_virtual_time - n['start_time'])
                            if time_diff < 0.15:
                                n['hit'] = True
                                self.score += 100
                                self.set_feedback("PERFECT!")
                                break
                            elif time_diff < 0.30:
                                n['hit'] = True
                                self.score += 50
                                self.set_feedback("GOOD")
                                break

                elif self.game_mode == "WAIT":
                    if next_note and note == next_note['note']:
                        next_note['hit'] = True
                        self.score += 100
                        self.set_feedback("HIT!")

            elif status == 128 or (status == 144 and velocity == 0):
                self.active_keys.discard(note)

        return next_note, is_waiting

    def set_feedback(self, text):
        self.feedback_text = text
        self.feedback_timer = time.time()

    def toggle_mode(self):
        self.game_mode = "FLOW" if self.game_mode == "WAIT" else "WAIT"
