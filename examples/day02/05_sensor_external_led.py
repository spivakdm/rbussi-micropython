"""External LED on when the right sensor sees black; 15-second test."""
from machine import Pin
from time import sleep_ms

RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
EXTERNAL_LED_GPIO = 26  # D2; confirm this contact is free on the shield.
RIGHT_BLACK = 1  # Black = 1, white = 0 on this robot.

sensor = Pin(RIGHT_GPIO, Pin.IN)
led = Pin(EXTERNAL_LED_GPIO, Pin.OUT, value=0)
try:
    for _ in range(150):
        raw = sensor.value()
        if raw == RIGHT_BLACK:
            led.on()
        else:
            led.off()
        print(raw, led.value())
        sleep_ms(100)
finally:
    led.off()
