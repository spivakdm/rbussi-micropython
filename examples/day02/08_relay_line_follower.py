"""Bounded relay follower: narrow black line between sensors on white.

Start centred with both sensors on white. Check all states with wheels
lifted before a floor trial. Both-white also occurs when the line is lost;
these two digital sensors cannot distinguish that case from being centred.
"""
from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms
from robot import RBussi

LEFT_GPIO = 34   # A3; verify by covering only the left sensor.
RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
LEFT_BLACK = 1   # Black = 1, white = 0 on this robot.
RIGHT_BLACK = 1  # Black = 1, white = 0 on this robot.
LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0
SPEED = 50
INNER_SPEED = 0
RUN_MS = 5000
SAMPLE_MS = 20

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    left = Pin(LEFT_GPIO, Pin.IN)
    right = Pin(RIGHT_GPIO, Pin.IN)
    start = ticks_ms()
    previous = None
    while ticks_diff(ticks_ms(), start) < RUN_MS:
        left_black = left.value() == LEFT_BLACK
        right_black = right.value() == RIGHT_BLACK

        if not left_black and not right_black:
            robot.motors(left=SPEED, right=SPEED)
            action = 'forward'
        elif left_black and not right_black:
            robot.motors(left=INNER_SPEED, right=SPEED)
            action = 'left'
        elif not left_black and right_black:
            robot.motors(left=SPEED, right=INNER_SPEED)
            action = 'right'
        else:
            robot.stop()
            print('Both sensors black: stopped')
            break

        if action != previous:
            print('L black:', int(left_black), 'R black:', int(right_black), action)
            previous = action
        sleep_ms(SAMPLE_MS)
finally:
    robot.close()
