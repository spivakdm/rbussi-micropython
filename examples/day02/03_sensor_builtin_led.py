"""Built-in LED on when the right sensor sees black; 15-second test."""
from machine import Pin
from time import sleep_ms

RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
BUILTIN_LED_GPIO = 2
RIGHT_BLACK = 1  # Black = 1, white = 0 on this robot.

sensor = Pin(RIGHT_GPIO, Pin.IN)
led = Pin(BUILTIN_LED_GPIO, Pin.OUT, value=0)
try:
    for _ in range(150):
        raw = sensor.value()
        black = raw == RIGHT_BLACK
        led.value(black)
        print(raw, int(black))
        sleep_ms(100)
finally:
    led.value(0)
