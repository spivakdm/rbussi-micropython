"""Right sensor: black = forward, white = backward.

Start with wheels lifted. Move paper beneath the sensor, not your hands
near the wheels. This demonstrates a condition, not line following.
"""
from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms
from robot import RBussi

RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
RIGHT_BLACK = 1  # Black = 1, white = 0 on this robot.
LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0
SPEED = 50
RUN_MS = 5000
SAMPLE_MS = 20

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    sensor = Pin(RIGHT_GPIO, Pin.IN)
    start = ticks_ms()
    previous = None
    while ticks_diff(ticks_ms(), start) < RUN_MS:
        raw = sensor.value()
        if raw == RIGHT_BLACK:
            robot.motors(left=SPEED, right=SPEED)
            action = 'forward'
        else:
            robot.motors(left=-SPEED, right=-SPEED)
            action = 'backward'
        if action != previous:
            print(raw, action)
            previous = action
        sleep_ms(SAMPLE_MS)
finally:
    robot.close()
