"""Blink an external LED five times.

Wire with power off: GPIO26 (D2) -> 470-ohm resistor -> LED anode (+).
LED cathode (-) -> GND. Confirm GPIO26 is free on the actual shield.
"""
from machine import Pin
from time import sleep_ms
from day02_settings import EXTERNAL_LED_GPIO

led = Pin(EXTERNAL_LED_GPIO, Pin.OUT, value=0)
try:
    for _ in range(5):
        led.on()
        sleep_ms(500)
        led.off()
        sleep_ms(500)
finally:
    led.off()
