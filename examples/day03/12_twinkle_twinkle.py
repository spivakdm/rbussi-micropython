"""Play the opening of Twinkle, Twinkle, Little Star. Motor power off."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; confirm free pin and a suitable passive piezo circuit.
C4 = 262
D4 = 294
E4 = 330
F4 = 349
G4 = 392
A4 = 440

# Each pair is (frequency in Hz, duration in ms).
# Frequency 0 represents a silent rest.

melody = [
    (C4, 300), (C4, 300), (G4, 300), (G4, 300),
    (A4, 300), (A4, 300), (G4, 600),
    (F4, 300), (F4, 300), (E4, 300), (E4, 300),
    (D4, 300), (D4, 300), (C4, 600),
]

pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)


def play_note(frequency, duration_ms):
    if frequency == 0:
        sound.duty_u16(0)
    else:
        sound.freq(frequency)
        sound.duty_u16(32768)
    sleep_ms(duration_ms)
    sound.duty_u16(0)


try:
    for frequency, duration_ms in melody:
        play_note(frequency, duration_ms)
        sleep_ms(40)
finally:
    # Always stop PWM, including after Ctrl+C.
    sound.duty_u16(0)
    sound.deinit()
    pin.value(0)
