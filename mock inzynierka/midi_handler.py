import pygame.midi
import mido
import sys

class MIDIHandler:
    def __init__(self):
        pygame.midi.init()
        self.input_device_id = None
        
        for i in range(pygame.midi.get_count()):
            info = pygame.midi.get_device_info(i)
            if info[2] and self.input_device_id is None: 
                self.input_device_id = i

        if self.input_device_id is None:
            print("[BŁĄD] Nie wykryto keyboardu MIDI!")
            pygame.midi.quit()
            sys.exit()

        self.midi_in = pygame.midi.Input(self.input_device_id)

    def read_events(self):
        """Pobiera zdarzenia z keyboardu i zwraca listę aktywnych nut."""
        events = []
        if self.midi_in.poll():
            for midi_event in self.midi_in.read(20):
                data, _ = midi_event
                status, note, velocity, _ = data
                events.append((status, note, velocity))
        return events

    def close(self):
        self.midi_in.close()
        pygame.midi.quit()

def load_midi_notes(filepath):
    """Parsuje plik .mid i zwraca posortowaną listę nut z czasem trwania."""
    mid = mido.MidiFile(filepath)
    notes = []
    active_notes = {}
    current_time = 0.0

    for msg in mid:
        current_time += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes[msg.note] = current_time
        elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)) and msg.note in active_notes:
            start = active_notes.pop(msg.note)
            duration = max(0.1, current_time - start)
            notes.append({
                'note': msg.note,
                'start_time': start,
                'duration': duration,
                'hit': False
            })

    notes.sort(key=lambda x: x['start_time'])
    return notes
