"""Right sensor: black = forward, white = backward.

Start with wheels lifted. Move paper beneath the sensor, not your hands
near the wheels. This demonstrates a condition, not line following.
No timer: stop with Ctrl+C or switch off motor power.
"""
from machine import Pin
from time import sleep_ms
from robot import RBussi

RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
RIGHT_BLACK = 1  # Black = 1, white = 0 on this robot.
LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0
SPEED = 50
SAMPLE_MS = 20

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    sensor = Pin(RIGHT_GPIO, Pin.IN)
    while True:
        raw = sensor.value()
        if raw == RIGHT_BLACK:
            robot.motors(left=SPEED, right=SPEED)
        else:
            robot.motors(left=-SPEED, right=-SPEED)
        sleep_ms(SAMPLE_MS)
finally:
    robot.close()
