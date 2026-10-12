"""External LED on when the right sensor sees black; 15-second test."""
from machine import Pin
from time import sleep_ms
import day02_settings as settings

settings.require_calibration()
sensor = Pin(settings.RIGHT_GPIO, Pin.IN)
led = Pin(settings.EXTERNAL_LED_GPIO, Pin.OUT, value=0)
try:
    for _ in range(150):
        raw = sensor.value()
        if raw == settings.RIGHT_BLACK:
            led.on()
        else:
            led.off()
        print(raw, led.value())
        sleep_ms(100)
finally:
    led.off()
