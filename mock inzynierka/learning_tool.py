class LearningTool:
    def __init__(self, preview_window=1.2):
        self.preview_window = preview_window

    def get_learning_cues(self, song_notes, virtual_time, game_mode, wrong_keys_timers):
        """
        Analizuje stan piosenki i zwraca wszystko, co jest potrzebne 
        do podświetlenia podpowiedzi (hintów), nadchodzących nut oraz błędów.
        Wszystkie przyszłe modyfikacje podpowiedzi (np. długość nuty) 
        będziesz dopisywać tylko tutaj!
        """
        # 1. Następna nuta do uderzenia
        next_note = next((n for n in song_notes if not n['hit']), None)

        # 2. Sprawdzenie czy jesteśmy w stanie oczekiwania (Wait Mode)
        is_waiting = False
        if game_mode == "WAIT" and next_note is not None:
            if virtual_time >= next_note['start_time']:
                is_waiting = True

        # 3. Nadchodzące nuty do podglądu (Preview)
        upcoming_notes = []
        for n in song_notes:
            if not n['hit']:
                time_until = n['start_time'] - virtual_time
                if 0 < time_until <= self.preview_window:
                    # Tutaj w przyszłości możesz też wyliczać np. długość nuty dla podpowiedzi
                    upcoming_notes.append(n)

        # 4. Aktywne błędy do czerwonego podświetlenia
        wrong_keys_active = set(wrong_keys_timers.keys())

        # Zwracamy czysty zestaw danych do wyświetlenia podpowiedzi
        return {
            "next_note": next_note,
            "is_waiting": is_waiting,
            "upcoming_notes": upcoming_notes,
            "wrong_keys": wrong_keys_active
        }
