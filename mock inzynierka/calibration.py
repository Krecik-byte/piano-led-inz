import os
import json
import time
import sys
import pygame

CONFIG_FILE = "config.json"

def run_calibration(screen, clock, midi_handler, width, height, font, font_big):
    step = 1
    min_note = None
    max_note = None

    print("[KALIBRACJA] Wciśnij skrajny LEWY klawisz na keyboardzie...")

    calibrating = True
    while calibrating:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                midi_handler.close()
                pygame.quit()
                sys.exit()

        events = midi_handler.read_events()
        for status, note, velocity in events:
            if status == 144 and velocity > 0:
                if step == 1:
                    min_note = note
                    step = 2
                    print(f"[KALIBRACJA] LEWY klawisz: {min_note}")
                    time.sleep(0.3)
                elif step == 2:
                    if note > min_note:
                        max_note = note
                        calibrating = False
                        print(f"[KALIBRACJA] PRAWY klawisz: {max_note}")

        screen.fill((20, 22, 30))
        if step == 1:
            txt1 = font_big.render("KROK 1: Wciśnij skrajny LEWY klawisz", True, (0, 220, 255))
            txt2 = font.render("Wykrywanie najniższego dźwięku klawiatury...", True, (180, 180, 180))
        else:
            txt1 = font_big.render("KROK 2: Wciśnij skrajny PRAWY klawisz", True, (255, 200, 0))
            txt2 = font.render(f"Lewy: {min_note} | Wykrywanie najwyższego dźwięku...", True, (180, 180, 180))

        screen.blit(txt1, (width // 2 - txt1.get_width() // 2, height // 2 - 40))
        screen.blit(txt2, (width // 2 - txt2.get_width() // 2, height // 2 + 10))

        pygame.display.flip()
        clock.tick(60)

    num_keys = max_note - min_note + 1
    config_data = {"min_note": min_note, "max_note": max_note, "num_keys": num_keys}
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)
        
    return min_note, num_keys

def get_keyboard_config(screen, clock, midi_handler, width, height, font, font_big):
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data["min_note"], data["num_keys"]
        except Exception as e:
            print(f"[CONFIG] Błąd pliku ({e}), uruchamiam kalibrację...")
            
    return run_calibration(screen, clock, midi_handler, width, height, font, font_big)
