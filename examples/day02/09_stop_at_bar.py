"""Drive straight and stop when BOTH sensors see a black transverse bar.

Adjust the sensor trimmers, then test with wheels lifted by moving the paper.
For a brief floor test, aim towards the printed bar from a short distance.
This example does not steer or follow a line.
No timer: both-black ends the run; Ctrl+C also requests cleanup.
"""
from machine import Pin
from time import sleep_ms
from robot import RBussi

LEFT_GPIO = 34   # A3; verify by covering only the left sensor.
RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
LEFT_BLACK = 1   # Black = 1, white = 0 on this robot.
RIGHT_BLACK = 1  # Black = 1, white = 0 on this robot.
LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0
SPEED = 50
SAMPLE_MS = 20

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    left = Pin(LEFT_GPIO, Pin.IN)
    right = Pin(RIGHT_GPIO, Pin.IN)

    while True:
        left_black = left.value() == LEFT_BLACK
        right_black = right.value() == RIGHT_BLACK

        if left_black and right_black:
            robot.stop()
            print('Black bar detected: stopped')
            break

        robot.motors(left=SPEED, right=SPEED)
        sleep_ms(SAMPLE_MS)
finally:
    robot.close()
