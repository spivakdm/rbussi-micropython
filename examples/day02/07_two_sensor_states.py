"""Read all four colour combinations without requesting movement."""
from machine import Pin
from time import sleep_ms
from robot import RBussi
import day02_settings as settings

settings.require_calibration()
robot = RBussi()
try:
    left = Pin(settings.LEFT_GPIO, Pin.IN)
    right = Pin(settings.RIGHT_GPIO, Pin.IN)
    for _ in range(100):
        left_black = left.value() == settings.LEFT_BLACK
        right_black = right.value() == settings.RIGHT_BLACK
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
