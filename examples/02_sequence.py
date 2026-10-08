"""Use after the instructor has checked forward/backward directions."""
from robot import RBussi
from time import sleep

speed = 50
with RBussi() as robot:
    robot.forward(speed=speed, seconds=0.5)
    sleep(0.5)
    robot.backward(speed=speed, seconds=0.5)
