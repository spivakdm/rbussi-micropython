"""Relay follower: narrow black line between sensors on white.

Start centred with both sensors on white. Check all states with wheels
lifted before a floor trial. Both-white also occurs when the line is lost;
these two digital sensors cannot distinguish that case from being centred.
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
INNER_SPEED = 0
SAMPLE_MS = 20

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    left = Pin(LEFT_GPIO, Pin.IN)
    right = Pin(RIGHT_GPIO, Pin.IN)
    while True:
        left_black = left.value() == LEFT_BLACK
        right_black = right.value() == RIGHT_BLACK

        if not left_black and not right_black:
            robot.motors(left=SPEED, right=SPEED)
        elif left_black and not right_black:
            robot.motors(left=INNER_SPEED, right=SPEED)
        elif not left_black and right_black:
            robot.motors(left=SPEED, right=INNER_SPEED)
        else:
            robot.stop()
            print('Both sensors black: stopped')
            break

        sleep_ms(SAMPLE_MS)
finally:
    robot.close()
