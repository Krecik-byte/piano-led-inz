import pygame
import pygame.midi
import math
import struct


WIDTH = 1100
HEIGHT = 280

pygame.init()
pygame.midi.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kompaktowa Klawiatura MIDI (Dopasowana szerokość)")
clock = pygame.time.Clock()

MIDI_START = 60  
NUM_KEYS = 24    

midi_out = None
for i in range(pygame.midi.get_count()):
    r = pygame.midi.get_device_info(i)
    device_name = r[1].decode('utf-8', errors='ignore')
    if r[3] and ("PianoVirtual" in device_name or "loopMIDI" in device_name):
        try:
            midi_out = pygame.midi.Output(i)
            print(f"[SUKCES] Połączono z wyjściem MIDI: {device_name} (ID {i})")
            break
        except Exception as e:
            print(f"[BŁĄD] Nie udało się otworzyć portu {i}: {e}")

if not midi_out:
    print("\n[OSTRZEŻENIE] Nie znaleziono portu 'PianoVirtual'! Upewnij się, że loopMIDI jest włączone.")

def midi_to_freq(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

sound_cache = {}
def get_note_sound(note):
    if note in sound_cache:
        return sound_cache[note]
    
    freq = midi_to_freq(note)
    duration = 3.0  # Dłuższy bufor dźwięku, żeby nuta brzmiała podczas trzymania
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    audio_data = bytearray()
    for s in range(num_samples):
        t = s / sample_rate
        # Delikatny obwiednia: łagodny start i bardzo wolne opadanie (sustain)
        env = min(1.0, t / 0.05) * math.exp(-0.3 * t)
        val = int(0.25 * 32767 * math.sin(2 * math.pi * freq * t) * env)
        audio_data.extend(struct.pack('<h', val))
        
    sound = pygame.mixer.Sound(buffer=bytes(audio_data))
    sound_cache[note] = sound
    return sound

key_rects = {}
white_count = sum(1 for i in range(NUM_KEYS) if (MIDI_START + i) % 12 not in [1, 3, 6, 8, 10])
w_width = WIDTH / max(white_count, 1)
w_height = 160
b_width = w_width * 0.6
b_height = 95

# 1. Białe klawisze
curr_w_x = 0
for i in range(NUM_KEYS):
    note = MIDI_START + i
    is_black = (note % 12) in [1, 3, 6, 8, 10]
    if not is_black:
        rect = pygame.Rect(curr_w_x, HEIGHT - w_height, w_width, w_height)
        key_rects[note] = {'rect': rect, 'is_black': False, 'pressed': False}
        curr_w_x += w_width

# 2. Czarne klawisze
curr_w_x = 0
for i in range(NUM_KEYS):
    note = MIDI_START + i
    is_black = (note % 12) in [1, 3, 6, 8, 10]
    if not is_black:
        curr_w_x += w_width
    else:
        rect_x = curr_w_x - (b_width / 2)
        rect = pygame.Rect(rect_x, HEIGHT - w_height, b_width, b_height)
        key_rects[note] = {'rect': rect, 'is_black': True, 'pressed': False}

print("\n--- KLAWIATURA O IDEALNEJ SZEROKOŚCI GOTOWA ---")

running = True
active_note = None
active_channel = None  # Przechowuje kanał aktualnie odtwarzanego dźwięku

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for note, data in sorted(key_rects.items(), key=lambda x: x[1]['is_black'], reverse=True):
                if data['rect'].collidepoint(pos):
                    active_note = note
                    data['pressed'] = True
                    if midi_out:
                        midi_out.note_on(note, 90)
                    
                    # Odtwarzamy dźwięk i zapamiętujemy kanał
                    sound = get_note_sound(note)
                    active_channel = sound.play()
                    break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if active_note is not None and active_note in key_rects:
                key_rects[active_note]['pressed'] = False
                if midi_out:
                    midi_out.note_off(active_note, 0)
                
                # Zatrzymujemy dźwięk natychmiast po puszczeniu klawisza myszy
                if active_channel:
                    active_channel.stop()
                    active_channel = None
                    
                active_note = None

    # Rysowanie interfejsu
    screen.fill((30, 30, 40))
    
    font = pygame.font.SysFont("Consolas", 14, bold=True)
    txt = font.render(f"Kompaktowa klawiatura (Szerokość: {WIDTH}px) -> loopMIDI + Dźwięk", True, (200, 200, 200))
    screen.blit(txt, (20, 15))

    # Rysuj białe klawisze
    for note, data in key_rects.items():
        if not data['is_black']:
            col = (100, 200, 255) if data['pressed'] else (245, 245, 245)
            pygame.draw.rect(screen, col, data['rect'])
            pygame.draw.rect(screen, (50, 50, 50), data['rect'], 1)

    # Rysuj czarne klawisze
    for note, data in key_rects.items():
        if data['is_black']:
            col = (60, 120, 180) if data['pressed'] else (30, 30, 30)
            pygame.draw.rect(screen, col, data['rect'])
            pygame.draw.rect(screen, (10, 10, 10), data['rect'], 1)

    pygame.display.flip()
    clock.tick(60)

if midi_out:
    midi_out.close()
pygame.midi.quit()
pygame.mixer.quit()
pygame.quit()