"""Extra task: three digital sensors and stepped relay steering.

Requires THREE connected sensors. The proposed centre sensor is A4/GPIO36.
Black = 1, white = 0. Start with the line under the centre sensor.
No timer. Unsupported patterns stop and end the run; Ctrl+C requests cleanup.
"""
from machine import Pin
from time import sleep_ms
from robot import RBussi

LEFT_GPIO = 34    # Existing A3 sensor; verify physical side.
CENTRE_GPIO = 36  # A4; proposed new sensor, not yet connected.
RIGHT_GPIO = 35   # Existing A2 sensor; verify physical side.
SPEED = 50
SLOW_SPEED = 30
INNER_SPEED = 0
LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0
SAMPLE_MS = 20

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    left = Pin(LEFT_GPIO, Pin.IN)
    centre = Pin(CENTRE_GPIO, Pin.IN)
    right = Pin(RIGHT_GPIO, Pin.IN)

    while True:
        left_black = left.value() == 1
        centre_black = centre.value() == 1
        right_black = right.value() == 1

        if not left_black and centre_black and not right_black:  # 010
            robot.motors(left=SPEED, right=SPEED)
        elif left_black and centre_black and not right_black:    # 110
            robot.motors(left=SLOW_SPEED, right=SPEED)
        elif left_black and not centre_black and not right_black:  # 100
            robot.motors(left=INNER_SPEED, right=SPEED)
        elif not left_black and centre_black and right_black:    # 011
            robot.motors(left=SPEED, right=SLOW_SPEED)
        elif not left_black and not centre_black and right_black:  # 001
            robot.motors(left=SPEED, right=INNER_SPEED)
        else:  # 000: no black; 111: broad bar; 101: ambiguous pattern.
            robot.stop()
            print('Stop pattern:', int(left_black), int(centre_black), int(right_black))
            break

        sleep_ms(SAMPLE_MS)
finally:
    robot.close()
