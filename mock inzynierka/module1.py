import mido
from mido import Message, MidiFile, MidiTrack

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Szkocka melodia "Auld Lang Syne" - bardzo prosta, idealna do powolnego grania na 1 rękę
melodia = [
    # Pierwsza fraza
    60, 65, 65, 65, 69, 67, 65, 67, 69, 65, 65, 69, 72, 74,
    # Druga fraza
    74, 72, 69, 69, 65, 67, 65, 67, 69, 65, 62, 62, 60, 65,
    # Refren
    74, 72, 69, 69, 65, 67, 65, 67, 74, 72, 69, 69, 72, 74,
    74, 72, 69, 69, 65, 67, 65, 67, 69, 65, 62, 62, 60, 65
]

first = True
for note in melodia:
    time_delay = 750 if first else 0  # Bardzo wolne, dostojne tempo
    first = False
    track.append(Message('note_on', note=note, velocity=80, time=time_delay))
    track.append(Message('note_off', note=note, velocity=0, time=600))  

mid.save("song.mid")
print("Gotowe! Wygenerowano plik song.mid z utworem Auld Lang Syne.")