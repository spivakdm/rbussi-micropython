"""Play the opening of Twinkle, Twinkle, Little Star. Motor power off."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; confirm free pin and a suitable passive piezo circuit.
# A4 = 440 Hz; doubling a frequency raises the pitch by one octave.
# These integer frequencies are rounded approximations of musical notes.
C4 = 262
D4 = 294
E4 = 330
F4 = 349
G4 = 392
A4 = 440

# Each pair is (frequency in Hz, duration in milliseconds).
# A frequency of 0 represents a silent rest, not PWM at 0 Hz.

melody = [
    (C4, 300), (C4, 300), (G4, 300), (G4, 300),
    (A4, 300), (A4, 300), (G4, 600),
    (F4, 300), (F4, 300), (E4, 300), (E4, 300),
    (D4, 300), (D4, 300), (C4, 600),
]

# Start LOW and create PWM in a silent state.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)


def play_note(frequency, duration_ms):
    if frequency == 0:
        # A rest lasts as long as a note but leaves the PWM drive off.
        sound.duty_u16(0)
    else:
        # Keep fill at about 50%; change frequency to select the pitch.
        sound.freq(frequency)
        sound.duty_u16(32768)
    try:
        # This simple player waits here until the note or rest is over.
        sleep_ms(duration_ms)
    finally:
        # Silence the output even if Ctrl+C interrupts this note.
        sound.duty_u16(0)


try:
    # Unpack each list item into its frequency and duration.
    for frequency, duration_ms in melody:
        play_note(frequency, duration_ms)
        # A small gap separates repeated notes so they can be heard individually.
        sleep_ms(40)
finally:
    # Run on completion, error or Ctrl+C: stop PWM, release it and leave LOW.
    sound.duty_u16(0)
    sound.deinit()
    pin.value(0)
