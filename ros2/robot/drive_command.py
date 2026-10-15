"""Validated motor requests. Units are PWM percent, not measured velocity."""
import json

MAX_SPEED = 60
MAX_DURATION_MS = 1000


def parse_drive(topic_suffix, payload):
    if topic_suffix == "move":
        commands = {
            b"forward": (40, 40, 1000),
            b"backward": (-40, -40, 1000),
            b"left": (-35, 35, 400),
            b"right": (35, -35, 400),
            b"stop": (0, 0, 0),
        }
        if payload not in commands:
            raise ValueError("Use forward, backward, left, right or stop")
        return commands[payload]
    data = json.loads(payload)
    left, right, duration = data['left'], data['right'], data['duration_ms']
    if any(type(value) is not int for value in (left, right, duration)):
        raise ValueError("Wheel command values must be integers")
    if not (-MAX_SPEED <= left <= MAX_SPEED and -MAX_SPEED <= right <= MAX_SPEED):
        raise ValueError("Wheel PWM must be within -60..60")
    if not 50 <= duration <= MAX_DURATION_MS:
        raise ValueError("Duration must be within 50..1000 ms")
    return left, right, duration
