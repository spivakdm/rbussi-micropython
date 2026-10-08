"""MicroPython movement library for the Wemos D1 R32 robot.

Speed: -100..100; positive values mean forward.
Right wheel: channel A, physically confirmed.
Left wheel: channel B. Forward movement confirmed with the default directions.
"""
from machine import Pin, PWM
from time import sleep_ms


def _number(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(name + ': expected a number')
    if not low <= value <= high:
        raise ValueError(name + ': outside the allowed range')
    return value


class RBussi:
    """Two-wheel controller with optional direction and PWM balance correction.

    left_scale/right_scale: 0..1, default 1. No measured-speed feedback.
    """
    def __init__(self, left_reversed=False, right_reversed=False,
                 left_scale=1.0, right_scale=1.0):
        # Validate before creating any GPIO or PWM objects.
        self._scale = (_number(left_scale, 'left_scale', 0, 1),
                       _number(right_scale, 'right_scale', 0, 1))
        self._closed = False
        self._pwm = []
        self._last = (0, 0)
        self._reversed = (left_reversed, right_reversed)
        # Array order: left wheel, right wheel.
        self._enable = [Pin(23, Pin.OUT, value=0), Pin(25, Pin.OUT, value=0)]
        self._brake = [Pin(12, Pin.OUT, value=1), Pin(13, Pin.OUT, value=1)]
        self._direction = [Pin(18, Pin.OUT, value=0), Pin(19, Pin.OUT, value=0)]
        try:
            for pin in self._enable:
                self._pwm.append(PWM(pin, freq=1000, duty_u16=0))
        except BaseException:
            self.close()
            raise

    def stop(self):
        """Stop both wheels. Safe to call repeatedly."""
        if self._closed:
            return
        for pwm in self._pwm:
            pwm.duty_u16(0)
        for brake in self._brake:
            brake.value(1)
        self._last = (0, 0)

    def motors(self, left, right):
        """Set speeds from -100 to 100 until the next command or stop().

        Per-wheel scales multiply PWM duty, not measured wheel velocity.
        For continuous movement, use try/finally with robot.stop().
        """
        if self._closed:
            raise RuntimeError('RBussi is already closed')
        try:
            speeds = (_number(left, 'left', -100, 100) * self._scale[0],
                      _number(right, 'right', -100, 100) * self._scale[1])
            if any(old * new < 0 for old, new in zip(self._last, speeds)):
                self.stop()
                sleep_ms(20)
            for i, speed in enumerate(speeds):
                pwm = self._pwm[i]
                if speed == 0:
                    pwm.duty_u16(0)
                    self._brake[i].value(1)
                else:
                    self._direction[i].value(int((speed < 0) != self._reversed[i]))
                    self._brake[i].value(0)
                    pwm.duty_u16(round(abs(speed) * 65535 / 100))
            self._last = speeds
        except BaseException:
            self.stop()
            raise

    def move(self, left, right, seconds=1):
        """Move for the specified duration (0..60 seconds), then stop."""
        try:
            seconds = _number(seconds, 'seconds', 0, 60)
            # A zero duration never enables the motors.
            if seconds == 0:
                return
            self.motors(left, right)
            sleep_ms(round(seconds * 1000))
        finally:
            self.stop()

    def _timed(self, speed, seconds, left_sign, right_sign):
        try:
            speed = _number(speed, 'speed', 0, 100)
            self.move(left_sign * speed, right_sign * speed, seconds)
        finally:
            self.stop()

    def forward(self, speed=50, seconds=1):
        """Move forward; speed 0..100, seconds 0..60."""
        self._timed(speed, seconds, 1, 1)

    def backward(self, speed=50, seconds=1):
        """Move backward."""
        self._timed(speed, seconds, -1, -1)

    def left(self, speed=50, seconds=0.3):
        """Turn left on the spot. Duration does not specify an exact angle."""
        self._timed(speed, seconds, -1, 1)

    def right(self, speed=50, seconds=0.3):
        """Turn right on the spot."""
        self._timed(speed, seconds, 1, -1)

    def close(self):
        """Stop the motors and release PWM before creating another RBussi."""
        if self._closed:
            return
        self.stop()
        for pwm in self._pwm:
            pwm.deinit()
        for pin in self._enable:
            pin.init(Pin.OUT, value=0)
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
