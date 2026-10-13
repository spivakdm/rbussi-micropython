"""Host checks of Day 2 decisions and cleanup; no physical hardware used."""
import contextlib
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples/day02'


class Day02Tests(unittest.TestCase):
    def run_example(self, filename, left_black=False, right_black=False,
                    inverted=False, fail_motors=False, fail_pin=False,
                    frames=None):
        source = (EXAMPLES / filename).read_text()
        left_black_level, right_black_level = 1, 1
        if inverted:
            # Simulate editing local constants for modules of opposite polarity.
            source = source.replace('LEFT_BLACK = 1', 'LEFT_BLACK = 0')
            source = source.replace('RIGHT_BLACK = 1', 'RIGHT_BLACK = 0')
            left_black_level = right_black_level = 0
        levels = {34: left_black_level if left_black else 1 - left_black_level,
                  35: right_black_level if right_black else 1 - right_black_level}
        events = []
        frames = frames or [(left_black, right_black)]
        frame_index = 0
        continuous_motion = filename.startswith(('06_', '08_', '09_'))

        def sleep_ms(duration):
            nonlocal frame_index
            if continuous_motion and frame_index == len(frames) - 1:
                raise KeyboardInterrupt()
            frame_index = min(frame_index + 1, len(frames) - 1)
            left, right = frames[frame_index]
            levels[34] = left_black_level if left else 1 - left_black_level
            levels[35] = right_black_level if right else 1 - right_black_level

        class Pin:
            IN, OUT = 0, 1
            def __init__(self, gpio, mode, value=0):
                if fail_pin:
                    raise OSError('disconnected sensor during initialization')
                self.gpio, self.mode, self.level = gpio, mode, value
            def value(self, value=None):
                if value is not None:
                    self.level = value
                    events.append(('pin', self.gpio, int(value)))
                return levels[self.gpio] if self.mode == self.IN else self.level
            def on(self):
                self.value(1)
            def off(self):
                self.value(0)

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

        modules = {'machine': types.SimpleNamespace(Pin=Pin),
                   'robot': types.SimpleNamespace(RBussi=Robot),
                   'time': types.SimpleNamespace(sleep_ms=sleep_ms)}
        try:
            with patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
                exec(compile(source, str(EXAMPLES / filename), 'exec'), {'__name__': '__main__'})
        except BaseException as error:
            return events, error
        return events, None

    def test_relay_states_for_both_polarities(self):
        for inverted in (False, True):
            for left, right, command in (
                (False, False, ('motors', 50, 50)),
                (True, False, ('motors', 0, 50)),
                (False, True, ('motors', 50, 0)),
                (True, True, ('stop',)),
            ):
                with self.subTest(inverted=inverted, left=left, right=right):
                    events, error = self.run_example('08_relay_line_follower.py', left, right, inverted)
                    if left and right:
                        self.assertIsNone(error)
                    else:
                        self.assertIsInstance(error, KeyboardInterrupt)
                    self.assertIn(command, events)
                    self.assertEqual(events[-1], ('close',))
                    if left and right:
                        self.assertFalse(any(event[0] == 'motors' for event in events))

    def test_reactive_forward_backward(self):
        for inverted in (False, True):
            for black, speed in ((False, -50), (True, 50)):
                events, error = self.run_example('06_black_forward_white_backward.py',
                                                 right_black=black, inverted=inverted)
                self.assertIsInstance(error, KeyboardInterrupt)
                self.assertIn(('motors', speed, speed), events)
                self.assertEqual(events[-1], ('close',))

    def test_interrupt_and_sensor_initialization_error_close_controller(self):
        for name in ('06_black_forward_white_backward.py', '08_relay_line_follower.py',
                     '09_stop_at_bar.py'):
            for failure in ('fail_motors', 'fail_pin'):
                events, error = self.run_example(name, **{failure: True})
                self.assertIsNotNone(error)
                self.assertEqual(events[-1], ('close',))

    def test_stop_bar_requires_both_black(self):
        for inverted in (False, True):
            for left, right in ((False, False), (True, False), (False, True), (True, True)):
                events, error = self.run_example('09_stop_at_bar.py', left, right, inverted)
                if left and right:
                    self.assertIsNone(error)
                    self.assertEqual(events[-2:], [('stop',), ('close',)])
                else:
                    self.assertIsInstance(error, KeyboardInterrupt)
                    self.assertEqual(events[-1], ('close',))
                self.assertEqual(('motors', 50, 50) in events, not (left and right))

    def test_stop_bar_ends_run_without_restarting(self):
        events, error = self.run_example('09_stop_at_bar.py',
                                        frames=[(False, False), (True, False),
                                                (True, True), (False, False)])
        self.assertIsNone(error)
        self.assertEqual(events, [('created',), ('motors', 50, 50),
                                  ('motors', 50, 50), ('stop',), ('close',)])

    def test_relay_stops_after_steering_without_restarting(self):
        events, error = self.run_example('08_relay_line_follower.py',
                                        frames=[(False, False), (True, False),
                                                (False, True), (True, True), (False, False)])
        self.assertIsNone(error)
        self.assertEqual(events, [('created',), ('motors', 50, 50),
                                  ('motors', 0, 50), ('motors', 50, 0),
                                  ('stop',), ('close',)])

    def test_sensor_led_if_else_and_final_off(self):
        for name, gpio in (('03_sensor_builtin_led.py', 2), ('05_sensor_external_led.py', 26)):
            for black in (False, True):
                events, error = self.run_example(name, right_black=black)
                self.assertIsNone(error)
                outputs = [event[2] for event in events if event[:2] == ('pin', gpio)]
                self.assertEqual(outputs[:-1], [int(black)] * 150)
                self.assertEqual(outputs[-1], 0)

    def test_nonmoving_examples_do_not_command_motors(self):
        for name in sorted(EXAMPLES.glob('0[1-5]_*.py')) + list(EXAMPLES.glob('07_*.py')):
            events, error = self.run_example(name.name)
            self.assertIsNone(error)
            self.assertFalse(any(event[0] == 'motors' for event in events))


if __name__ == '__main__':
    unittest.main()
