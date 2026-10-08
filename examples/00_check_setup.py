"""Check MicroPython and RBussi without starting the motors."""
import sys
from robot import RBussi

print(sys.implementation)
with RBussi() as robot:
    robot.stop()
print('RBussi ready. No movement requested.')
