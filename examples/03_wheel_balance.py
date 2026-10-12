"""Short wheel-balance trial. Adjust one scale between runs.

Test wheels lifted first, then use the marked floor area with cable slack.
Both scales start neutral; record your own robot's values.
"""
from robot import RBussi

LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    robot.move(left=50, right=50, seconds=0.5)
finally:
    robot.close()
