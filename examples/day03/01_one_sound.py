"""A short tone: use a suitable passive piezo; motor power off."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; confirm it is free and the piezo circuit is suitable.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)
try:
    sound.duty_u16(32768)  # Approximately 50% fill ratio.
    sleep_ms(200)
finally:
    sound.duty_u16(0)
    sound.deinit()
    pin.value(0)
