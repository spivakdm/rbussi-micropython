"""First movement. Lift the wheels and connect the motor battery before F5."""
from robot import RBussi

with RBussi() as robot:
    robot.forward(speed=50, seconds=0.5)
    # For subsequent experiments, uncomment one command:
    # robot.backward(speed=50, seconds=0.5)
    # robot.left(speed=50, seconds=0.3)
    # robot.right(speed=50, seconds=0.3)
# Leaving the with block stops the motors, including on errors or Ctrl+C.
