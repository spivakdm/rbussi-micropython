"""Independent timed wheel commands. Test with wheels lifted first."""
from robot import RBussi
from time import sleep_ms

robot = RBussi()
try:
    robot.move(left=50, right=50, seconds=0.3)
    sleep_ms(500)
    # Different duties normally produce a curve; observe your robot.
    robot.move(left=40, right=55, seconds=0.3)
finally:
    robot.close()
