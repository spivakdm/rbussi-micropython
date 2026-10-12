"""Built-in LED on when the right sensor sees black; 15-second test."""
from machine import Pin
from time import sleep_ms
import day02_settings as settings

settings.require_calibration()
sensor = Pin(settings.RIGHT_GPIO, Pin.IN)
led = Pin(settings.BUILTIN_LED_GPIO, Pin.OUT, value=0)
try:
    for _ in range(150):
        raw = sensor.value()
        black = raw == settings.RIGHT_BLACK
        led.value(black)
        print(raw, int(black))
        sleep_ms(100)
finally:
    led.value(0)
