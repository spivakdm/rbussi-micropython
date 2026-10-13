"""Print raw D0 levels for 15 seconds. No movement requested."""
from machine import Pin
from time import sleep_ms
from robot import RBussi

LEFT_GPIO = 34   # A3; verify by covering only the left sensor.
RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.

robot = RBussi()
try:
    left = Pin(LEFT_GPIO, Pin.IN)
    right = Pin(RIGHT_GPIO, Pin.IN)
    print('Left / A3, right / A2: white, black, then cover one sensor at a time')
    for _ in range(60):
        print(left.value(), right.value())
        sleep_ms(250)
finally:
    robot.close()
