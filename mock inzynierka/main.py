import sys
import time
import pygame
import serial

from midi_handler import MIDIHandler, load_midi_notes
from calibration import get_keyboard_config, run_calibration
from game_engine import GameEngine

pygame.init()

# Konfiguracja okna
WIDTH, HEIGHT = 1100, 750
KEYBOARD_HEIGHT = 160
HIT_LINE_Y = HEIGHT - KEYBOARD_HEIGHT
FALL_SPEED = 280
NUM_LEDS = 144
ACTIVE_LEDS = 122

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Hero - System Wspomagania Nauki Gry na Pianinie")

font = pygame.font.SysFont("Consolas", 18, bold=True)
font_big = pygame.font.SysFont("Consolas", 28, bold=True)
clock = pygame.time.Clock()

# Inicjalizacja MIDI i kalibracji
midi_handler = MIDIHandler()
MIDI_START, NUM_KEYS = get_keyboard_config(screen, clock, midi_handler, WIDTH, HEIGHT, font, font_big)
led_width = WIDTH / NUM_KEYS

# Inicjalizacja portu szeregowego do ESP32
try:
    ser = serial.Serial("COM3", 115200, timeout=0.01)  # Zmień COM3 na swój port jeśli inny!
    time.sleep(2)
    print("[ESP32] Połączono pomyślnie z taśmą LED.")
except Exception as e:
    ser = None
    print(f"[ESP32] Błąd połączenia z portem szeregowym: {e}")

# Ładowanie piosenki
MIDI_FILE = "song.mid"
try:
    song_notes = load_midi_notes(MIDI_FILE)
    print(f"Załadowano {len(song_notes)} nut z {MIDI_FILE}")
except Exception as e:
    print(f"Błąd pliku {MIDI_FILE}: {e}")
    song_notes = [
        {'note': MIDI_START + 12, 'start_time': 1.0, 'duration': 0.4, 'hit': False},
        {'note': MIDI_START + 14, 'start_time': 2.0, 'duration': 0.4, 'hit': False},
    ]

engine = GameEngine(song_notes)
BLACK_KEYS = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]

# Główna pętla programu
last_real_time = time.time()
try:
    while True:
        now = time.time()
        dt = now - last_real_time
        last_real_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    MIDI_START, NUM_KEYS = run_calibration(screen, clock, midi_handler, WIDTH, HEIGHT, font, font_big)
                    led_width = WIDTH / NUM_KEYS
                elif event.key == pygame.K_m:
                    engine.toggle_mode()

        midi_events = midi_handler.read_events()
        next_note, is_waiting = engine.update(dt, midi_events)

       # Wysyłanie stanu klawiszy do ESP32
        # Wysyłanie stanu klawiszy i podpowiedzi do ESP32
        if ser and ser.is_open:
            pressed_notes = list(engine.active_keys)
            
            # Zbieramy klawisze naciśnięte przez użytkownika
            user_indices = []
            for note in pressed_notes:
                mapped_led = int((note - MIDI_START) / NUM_KEYS * ACTIVE_LEDS)
                key_index = (NUM_LEDS - 1) - mapped_led
                if 0 <= key_index < NUM_LEDS:
                    user_indices.append(key_index)

            # Sprawdzamy czy mamy podpowiedź (w trybie WAIT)
            hint_index = -1
            if next_note and is_waiting:
                h_note = next_note['note']
                mapped_hint = int((h_note - MIDI_START) / NUM_KEYS * ACTIVE_LEDS)
                hint_index = (NUM_LEDS - 1) - mapped_hint

            # Tworzymy komunikat dla ESP32 w formacie: "uzytkownik:10,12|podpowiedz:45" albo prostszym
            # Przekażmy to jako: "P:10,12|H:45\n" lub po prostu wyślijmy osobno.
            # Zróbmy prosty format tekstowy rozdzielany średnikiem: "u10,12;h45\n"
            
            u_str = ",".join(map(str, user_indices)) if user_indices else "-1"
            h_str = str(hint_index) if hint_index != -1 else "-1"
            
            message = f"U:{u_str}|H:{h_str}\n"
            ser.write(message.encode("utf-8"))

        # RYSOWANIE GRAFIKI
        screen.fill((15, 15, 20))

        # Spadające nuty
        for n in engine.song_notes:
            key_idx = n['note'] - MIDI_START
            if 0 <= key_idx < NUM_KEYS:
                time_until_hit = n['start_time'] - engine.song_virtual_time
                y_pos = HIT_LINE_Y - (time_until_hit * FALL_SPEED)
                note_height = n['duration'] * FALL_SPEED

                if -note_height <= y_pos <= HEIGHT:
                    x_pos = key_idx * led_width
                    if n == next_note and is_waiting:
                        n_color = (255, 180, 0)
                    elif n['hit']:
                        n_color = (60, 220, 100)
                    else:
                        n_color = (80, 160, 255)

                    rect = pygame.Rect(x_pos + 1, y_pos - note_height, led_width - 2, note_height)
                    pygame.draw.rect(screen, n_color, rect, border_radius=4)

        # Linia trafienia
        line_color = (255, 200, 0) if is_waiting else (255, 60, 60)
        pygame.draw.line(screen, line_color, (0, HIT_LINE_Y), (WIDTH, HIT_LINE_Y), 4 if is_waiting else 3)

        # Klawiatura
        for i in range(NUM_KEYS):
            n_num = MIDI_START + i
            is_black = BLACK_KEYS[n_num % 12]
            is_pressed = n_num in engine.active_keys
            x = i * led_width

            if is_pressed:
                col = (0, 220, 255)
            elif next_note and is_waiting and n_num == next_note['note']:
                col = (255, 220, 0)
            else:
                col = (40, 40, 45) if is_black else (230, 230, 230)

            h = 100 if is_black else KEYBOARD_HEIGHT
            rect = pygame.Rect(x + 1, HIT_LINE_Y, led_width - 2, h)
            pygame.draw.rect(screen, col, rect, border_radius=2)

        # HUD
        score_surf = font.render(f"PUNKTY: {engine.score}", True, (255, 255, 255))
        screen.blit(score_surf, (20, 20))

        mode_col = (255, 200, 0) if engine.game_mode == "WAIT" else (0, 220, 255)
        mode_surf = font.render(f"TRYB: {engine.game_mode} [M]", True, mode_col)
        screen.blit(mode_surf, (20, 45))

        if is_waiting:
            wait_surf = font.render(">>> OCZEKIWANIE NA WCIŚNIĘCIE KRAWĘDZI KLAWISZA <<<", True, (255, 200, 0))
            screen.blit(wait_surf, (WIDTH // 2 - wait_surf.get_width() // 2, 20))

        info_surf = font.render("[R] Kalibracja | [M] Tryb", True, (120, 120, 140))
        screen.blit(info_surf, (WIDTH - 250, 20))

        if time.time() - engine.feedback_timer < 0.6 and engine.feedback_text:
            col = (0, 255, 120) if engine.feedback_text in ["PERFECT!", "HIT!"] else (255, 200, 0)
            fb_surf = font_big.render(engine.feedback_text, True, col)
            screen.blit(fb_surf, (WIDTH // 2 - 40, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

except KeyboardInterrupt:
    pass
finally:
    if 'ser' in locals() and ser and ser.is_open:
        ser.close()
    midi_handler.close()
    pygame.quit()