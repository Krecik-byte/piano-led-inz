import mido
from mido import Message, MidiFile, MidiTrack

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Tempo i nuty dla "Wlazł kotek na płotek"
# Nuty MIDI: G4(67), E4(64), E4(64), F4(65), D4(62), D4(62), C4(60), E4(64), G4(67)
melodia = [67, 64, 64, 65, 62, 62, 60, 64, 67]

first = True
for note in melodia:
    time_delay = 960 if first else 0  
    first = False
    track.append(Message('note_on', note=note, velocity=80, time=time_delay))
    track.append(Message('note_off', note=note, velocity=0, time=480))  

mid.save("song.mid")
print("Gotowe! Wygenerowano plik song.mid z banalną melodią.")
