"""Host checks of Day 2 decisions and cleanup; no physical hardware used."""
import contextlib
import importlib.util
import io
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples/day02'


def load_settings():
    spec = importlib.util.spec_from_file_location('day02_settings', EXAMPLES / 'day02_settings.py')
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    return settings


class Day02Tests(unittest.TestCase):
    def run_example(self, filename, left_black=False, right_black=False,
                    inverted=False, fail_motors=False, fail_pin=False,
                    calibrated=True, frames=None):
        settings = load_settings()
        if calibrated:
            settings.LEFT_WHITE = int(inverted)
            settings.LEFT_BLACK = int(not inverted)
            # Deliberately use opposite polarities for the two sensors.
            settings.RIGHT_WHITE = int(not inverted)
            settings.RIGHT_BLACK = int(inverted)
        levels = {settings.LEFT_GPIO: settings.LEFT_BLACK if left_black else settings.LEFT_WHITE,
                  settings.RIGHT_GPIO: settings.RIGHT_BLACK if right_black else settings.RIGHT_WHITE}
        events = []
        frames = frames or [(left_black, right_black)]
        frame_index = 0

        def sleep_ms(duration):
            nonlocal frame_index
            frame_index = min(frame_index + 1, len(frames) - 1)
            left, right = frames[frame_index]
            levels[settings.LEFT_GPIO] = settings.LEFT_BLACK if left else settings.LEFT_WHITE
            levels[settings.RIGHT_GPIO] = settings.RIGHT_BLACK if right else settings.RIGHT_WHITE

        class Pin:
            IN, OUT = 0, 1
            def __init__(self, gpio, mode, value=0):
                if fail_pin:
                    raise OSError('disconnected sensor during initialization')
                self.gpio, self.mode, self.level = gpio, mode, value
            def value(self, value=None):
                if value is not None:
                    self.level = value
                return levels[self.gpio] if self.mode == self.IN else self.level
            def on(self):
                self.level = 1
            def off(self):
                self.level = 0

        class Robot:
            def __init__(self, **kwargs):
                events.append(('created',))
            def motors(self, left, right):
                events.append(('motors', left, right))
                if fail_motors:
                    raise KeyboardInterrupt()
            def stop(self):
                events.append(('stop',))
            def close(self):
                events.append(('close',))

        clock = iter([0] + [i * settings.SAMPLE_MS for i in range(len(frames))]
                     + [settings.RUN_MS])
        modules = {'machine': types.SimpleNamespace(Pin=Pin),
                   'robot': types.SimpleNamespace(RBussi=Robot),
                   'day02_settings': settings,
                   'time': types.SimpleNamespace(ticks_ms=lambda: next(clock),
                                                 ticks_diff=lambda now, start: now - start,
                                                 sleep_ms=sleep_ms)}
        try:
            with patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(EXAMPLES / filename))
        except BaseException as error:
            return events, error
        return events, None

    def test_relay_states_with_independent_sensor_polarities(self):
        for inverted in (False, True):
            for left, right, command in (
                (False, False, ('motors', 50, 50)),
                (True, False, ('motors', 0, 50)),
                (False, True, ('motors', 50, 0)),
                (True, True, ('stop',)),
            ):
                with self.subTest(inverted=inverted, left=left, right=right):
                    events, error = self.run_example('08_relay_line_follower.py', left, right, inverted)
                    self.assertIsNone(error)
                    self.assertIn(command, events)
                    self.assertEqual(events[-1], ('close',))
                    if left and right:
                        self.assertFalse(any(event[0] == 'motors' for event in events))

    def test_reactive_forward_backward(self):
        for inverted in (False, True):
            for black, speed in ((False, -50), (True, 50)):
                events, error = self.run_example('06_black_forward_white_backward.py',
                                                 right_black=black, inverted=inverted)
                self.assertIsNone(error)
                self.assertIn(('motors', speed, speed), events)
                self.assertEqual(events[-1], ('close',))

    def test_missing_calibration_never_initializes_motors(self):
        for name in ('06_black_forward_white_backward.py', '08_relay_line_follower.py',
                     '09_stop_at_bar.py'):
            events, error = self.run_example(name, calibrated=False)
            self.assertIsInstance(error, ValueError)
            self.assertEqual(events, [])

    def test_interrupt_and_sensor_initialization_error_close_controller(self):
        for name in ('06_black_forward_white_backward.py', '08_relay_line_follower.py',
                     '09_stop_at_bar.py'):
            for failure in ('fail_motors', 'fail_pin'):
                events, error = self.run_example(name, **{failure: True})
                self.assertIsNotNone(error)
                self.assertEqual(events[-1], ('close',))

    def test_identical_colour_levels_are_rejected(self):
        settings = load_settings()
        settings.LEFT_WHITE = settings.LEFT_BLACK = 0
        settings.RIGHT_WHITE, settings.RIGHT_BLACK = 0, 1
        with self.assertRaises(ValueError):
            settings.require_calibration()

    def test_stop_bar_requires_both_black(self):
        for inverted in (False, True):
            for left, right in ((False, False), (True, False), (False, True), (True, True)):
                events, error = self.run_example('09_stop_at_bar.py', left, right, inverted)
                self.assertIsNone(error)
                self.assertEqual(events[-2:], [('stop',), ('close',)])
                self.assertEqual(('motors', 50, 50) in events, not (left and right))

    def test_stop_bar_ends_run_without_restarting(self):
        events, error = self.run_example('09_stop_at_bar.py',
                                        frames=[(False, False), (True, False),
                                                (True, True), (False, False)])
        self.assertIsNone(error)
        self.assertEqual(events, [('created',), ('motors', 50, 50),
                                  ('motors', 50, 50), ('stop',), ('close',)])

    def test_nonmoving_examples_do_not_command_motors(self):
        for name in sorted(EXAMPLES.glob('0[1-5]_*.py')) + list(EXAMPLES.glob('07_*.py')):
            events, error = self.run_example(name.name)
            self.assertIsNone(error)
            self.assertFalse(any(event[0] == 'motors' for event in events))


if __name__ == '__main__':
    unittest.main()
