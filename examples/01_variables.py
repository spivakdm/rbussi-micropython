"""Change one parameter, predict the result, then run a short trial."""
from robot import RBussi

speed = 50
duration = 0.5
print('Speed:', speed, 'Duration:', duration)
robot = RBussi()
try:
    robot.forward(speed=speed, seconds=duration)
finally:
    robot.close()
