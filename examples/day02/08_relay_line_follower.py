"""Bounded relay follower: narrow black line between sensors on white.

Start centred with both sensors on white. Check all states with wheels
lifted before a floor trial. Both-white also occurs when the line is lost;
these two digital sensors cannot distinguish that case from being centred.
"""
from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms
from robot import RBussi
import day02_settings as settings

settings.require_calibration()
robot = RBussi(left_scale=settings.LEFT_SCALE, right_scale=settings.RIGHT_SCALE)
try:
    left = Pin(settings.LEFT_GPIO, Pin.IN)
    right = Pin(settings.RIGHT_GPIO, Pin.IN)
    start = ticks_ms()
    previous = None
    while ticks_diff(ticks_ms(), start) < settings.RUN_MS:
        left_black = left.value() == settings.LEFT_BLACK
        right_black = right.value() == settings.RIGHT_BLACK

        if not left_black and not right_black:
            robot.motors(left=settings.SPEED, right=settings.SPEED)
            action = 'forward'
        elif left_black and not right_black:
            robot.motors(left=settings.INNER_SPEED, right=settings.SPEED)
            action = 'left'
        elif not left_black and right_black:
            robot.motors(left=settings.SPEED, right=settings.INNER_SPEED)
            action = 'right'
        else:
            robot.stop()
            print('Both sensors black: stopped')
            break

        if action != previous:
            print('L black:', int(left_black), 'R black:', int(right_black), action)
            previous = action
        sleep_ms(settings.SAMPLE_MS)
finally:
    robot.close()
