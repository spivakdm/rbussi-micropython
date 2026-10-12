"""Blink the built-in GPIO2 LED five times. No motor commands."""
from machine import Pin
from time import sleep_ms
from day02_settings import BUILTIN_LED_GPIO

led = Pin(BUILTIN_LED_GPIO, Pin.OUT, value=0)
try:
    for _ in range(5):
        led.value(1)
        sleep_ms(500)
        led.value(0)
        sleep_ms(500)
finally:
    led.value(0)
