"""Update wheel commands without a built-in duration. Wheels lifted first."""
from robot import RBussi
from time import sleep_ms

with RBussi() as robot:
    robot.motors(left=40, right=55)
    sleep_ms(300)
    robot.motors(left=55, right=40)
    sleep_ms(300)
    robot.stop()
# Leaving the block also stops and releases the controller.
