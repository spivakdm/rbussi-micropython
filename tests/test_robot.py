"""Host checks for failure paths without running motors."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

class Pin:
    OUT = 1
    def __init__(self, gpio, mode=None, value=0):
        self.gpio, self.level = gpio, value
    def value(self, value=None):
        if value is not None:
            self.level = value
        return self.level
    def init(self, mode, value):
        self.level = value

class PWM:
    def __init__(self, pin, freq, duty_u16):
        self.pin, self.duty = pin, duty_u16
    def duty_u16(self, value):
        self.duty = value
    def deinit(self):
        self.duty = 0

spec = importlib.util.spec_from_file_location('robot_under_test', Path(__file__).parents[1] / 'robot.py')
module = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {'machine': types.SimpleNamespace(Pin=Pin, PWM=PWM),
                              'time': types.SimpleNamespace(sleep_ms=lambda ms: None)}):
    spec.loader.exec_module(module)

class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.robot = module.RBussi()
    def assertStopped(self):
        self.assertTrue(all(p.duty == 0 for p in self.robot._pwm))
        self.assertTrue(all(p.value() == 1 for p in self.robot._brake))
    def test_interrupt_during_movement_stops(self):
        with patch.object(module, 'sleep_ms', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.robot.forward()
        self.assertStopped()
    def test_bad_second_speed_stops_existing_movement(self):
        self.robot.motors(50, 50)
        with self.assertRaises(ValueError):
            self.robot.motors(60, 101)
        self.assertStopped()
    def test_non_finite_time_stops(self):
        for bad in (float('nan'), float('inf'), -1, '1'):
            self.robot.motors(50, 50)
            with self.assertRaises(ValueError):
                self.robot.move(50, 50, bad)
            self.assertStopped()
    def test_context_exception_stops(self):
        with self.assertRaises(RuntimeError):
            with self.robot:
                self.robot.motors(50, 50)
                raise RuntimeError('student code failed')
        self.assertStopped()
        self.assertTrue(self.robot._closed)
    def test_zero_time_never_starts(self):
        with patch.object(self.robot, 'motors') as motors:
            self.robot.forward(seconds=0)
            motors.assert_not_called()
        self.assertStopped()
    def test_direction_change_stops_before_delay(self):
        self.robot.motors(50, 50)
        with patch.object(module, 'sleep_ms', side_effect=lambda ms: self.assertStopped()) as wait:
            self.robot.motors(-50, 50)
        wait.assert_called_once_with(20)
        self.robot.stop()

    def test_calibration_applies_to_timed_and_reverse_commands(self):
        with module.RBussi(left_scale=0.8, right_scale=1.0) as robot:
            with patch.object(module, 'sleep_ms', side_effect=lambda ms: self.assertEqual(
                    [p.duty for p in robot._pwm],
                    [round(40 * 65535 / 100), round(50 * 65535 / 100)])):
                robot.forward(speed=50, seconds=0.5)
            robot.motors(-50, -50)
            self.assertEqual([p.duty for p in robot._pwm],
                             [round(40 * 65535 / 100), round(50 * 65535 / 100)])
            self.assertEqual([p.value() for p in robot._direction], [1, 1])

    def test_zero_scale_brakes_disabled_wheel(self):
        with module.RBussi(left_scale=0) as robot:
            robot.motors(100, 50)
            self.assertEqual(robot._pwm[0].duty, 0)
            self.assertEqual(robot._brake[0].value(), 1)
            self.assertGreater(robot._pwm[1].duty, 0)

    def test_bad_calibration_never_initializes_hardware(self):
        for field in ('left_scale', 'right_scale'):
            for bad in (-0.1, 1.1, True, '0.9', float('nan'), float('inf')):
                with patch.object(module, 'Pin') as pin:
                    with self.assertRaises(ValueError):
                        module.RBussi(**{field: bad})
                    pin.assert_not_called()

if __name__ == '__main__':
    unittest.main()
