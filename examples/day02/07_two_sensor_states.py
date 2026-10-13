"""Read all four colour combinations without requesting movement."""
from machine import Pin
from time import sleep_ms
from robot import RBussi

LEFT_GPIO = 34   # A3; verify by covering only the left sensor.
RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
LEFT_BLACK = 1   # Black = 1, white = 0 on this robot.
RIGHT_BLACK = 1  # Black = 1, white = 0 on this robot.

robot = RBussi()
try:
    left = Pin(LEFT_GPIO, Pin.IN)
    right = Pin(RIGHT_GPIO, Pin.IN)
    for _ in range(100):
        left_black = left.value() == LEFT_BLACK
        right_black = right.value() == RIGHT_BLACK
        if not left_black and not right_black:
            action = 'forward (or line missing: same readings)'
        elif left_black and not right_black:
            action = 'steer left'
        elif not left_black and right_black:
            action = 'steer right'
        else:
            action = 'stop'
        print('L:', 'black' if left_black else 'white',
              'R:', 'black' if right_black else 'white', action)
        sleep_ms(200)
finally:
    robot.close()
