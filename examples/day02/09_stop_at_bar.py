"""Drive straight and stop when BOTH sensors see a black transverse bar.

Calibrate first, then test with wheels lifted by moving the paper.
For a brief floor test, aim towards the printed bar from a short distance.
This example does not steer or follow a line.
"""
from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms
from robot import RBussi
import day02_settings as settings

MAX_RUN_MS = 1000  # Short fallback for this exercise; not a distance command.

settings.require_calibration()
robot = RBussi(left_scale=settings.LEFT_SCALE, right_scale=settings.RIGHT_SCALE)
try:
    left = Pin(settings.LEFT_GPIO, Pin.IN)
    right = Pin(settings.RIGHT_GPIO, Pin.IN)
    start = ticks_ms()

    while ticks_diff(ticks_ms(), start) < min(MAX_RUN_MS, settings.RUN_MS):
        left_black = left.value() == settings.LEFT_BLACK
        right_black = right.value() == settings.RIGHT_BLACK

        if left_black and right_black:
            robot.stop()
            print('Black bar detected: stopped')
            break

        robot.motors(left=settings.SPEED, right=settings.SPEED)
        sleep_ms(settings.SAMPLE_MS)
    else:
        robot.stop()
        print('Time limit reached: stopped')
finally:
    robot.close()
