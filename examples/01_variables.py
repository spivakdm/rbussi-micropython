"""Change one parameter, predict the result, then run a short trial."""
from robot import RBussi

speed = 50
duration = 0.5
print('Speed:', speed, 'Duration:', duration)
with RBussi() as robot:
    robot.forward(speed=speed, seconds=duration)
