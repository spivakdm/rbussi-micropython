"""First movement. Lift the wheels and connect the motor battery before F5."""
from robot import RBussi

robot = RBussi()
try:
    robot.forward(speed=50, seconds=0.5)
    # For subsequent experiments, uncomment one command:
    # robot.backward(speed=50, seconds=0.5)
    # robot.left(speed=50, seconds=0.3)
    # robot.right(speed=50, seconds=0.3)
finally:
    robot.close()
# The finally block stops the motors and releases PWM, including on Ctrl+C.
