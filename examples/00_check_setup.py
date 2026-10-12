"""Check MicroPython and RBussi without starting the motors."""
import sys
from robot import RBussi

print(sys.implementation)
robot = RBussi()
try:
    robot.stop()
finally:
    robot.close()
print('RBussi ready. No movement requested.')
