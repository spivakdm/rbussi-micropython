"""A local function and a three-note sequence."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; use a suitable passive piezo circuit.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)


def beep(frequency, duration_ms):
    sound.freq(frequency)
    sound.duty_u16(32768)
    try:
        sleep_ms(duration_ms)
    finally:
        sound.duty_u16(0)


try:
    for frequency in [1000, 1500, 2000]:
        beep(frequency, 200)
        sleep_ms(200)
finally:
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    sound.deinit()
    pin.value(0)
