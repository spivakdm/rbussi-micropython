"""Right sensor: black = forward, white = backward.

Start with wheels lifted. Move paper beneath the sensor, not your hands
near the wheels. This demonstrates a condition, not line following.
"""
from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms
from robot import RBussi
import day02_settings as settings

settings.require_calibration()
robot = RBussi(left_scale=settings.LEFT_SCALE, right_scale=settings.RIGHT_SCALE)
try:
    sensor = Pin(settings.RIGHT_GPIO, Pin.IN)
    start = ticks_ms()
    previous = None
    while ticks_diff(ticks_ms(), start) < settings.RUN_MS:
        raw = sensor.value()
        if raw == settings.RIGHT_BLACK:
            robot.motors(left=settings.SPEED, right=settings.SPEED)
            action = 'forward'
        else:
            robot.motors(left=-settings.SPEED, right=-settings.SPEED)
            action = 'backward'
        if action != previous:
            print(raw, action)
            previous = action
        sleep_ms(settings.SAMPLE_MS)
finally:
    robot.close()
