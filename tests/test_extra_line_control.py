"""Host decision checks for proposed three/five-sensor hardware extensions."""
import contextlib
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples/day02'


class ExtraLineControlTests(unittest.TestCase):
    def run_controller(self, name, frames, kp=None, fail_pin=False, fail_motor=False):
        gpios = [39, 34, 36, 35, 4] if name.startswith('10_') else [34, 36, 35]
        source = (EXAMPLES / name).read_text()
        if kp is not None:
            source = source.replace('KP = 15', 'KP = ' + str(kp))
        events = []
        frame = 0

        class Pin:
            IN = 0
            def __init__(self, gpio, mode):
                if fail_pin:
                    raise OSError('sensor initialization failed')
                self.index = gpios.index(gpio)
            def value(self):
                return frames[frame][self.index]

        class Robot:
            def __init__(self, **kwargs):
                events.append(('created',))
            def motors(self, left, right):
                events.append(('motors', left, right))
                if fail_motor:
                    raise KeyboardInterrupt()
            def stop(self):
                events.append(('stop',))
            def close(self):
                events.append(('close',))

        def sleep_ms(duration):
            nonlocal frame
            if frame == len(frames) - 1:
                raise KeyboardInterrupt()
            frame += 1

        modules = {'machine': types.SimpleNamespace(Pin=Pin),
                   'robot': types.SimpleNamespace(RBussi=Robot),
                   'time': types.SimpleNamespace(sleep_ms=sleep_ms)}
        error = None
        try:
            with patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
                exec(compile(source, str(EXAMPLES / name), 'exec'), {'__name__': '__main__'})
        except BaseException as caught:
            error = caught
        return events, error

    def test_all_eight_relay_states(self):
        states = [([0, 1, 0], (50, 50)), ([1, 1, 0], (30, 50)),
                  ([1, 0, 0], (0, 50)), ([0, 1, 1], (50, 30)),
                  ([0, 0, 1], (50, 0)), ([0, 0, 0], None),
                  ([1, 1, 1], None), ([1, 0, 1], None)]
        for readings, speeds in states:
            with self.subTest(readings=readings):
                events, error = self.run_controller('11_relay_three_sensors.py', [readings])
                if speeds is None:
                    self.assertIsNone(error)
                    self.assertEqual(events, [('created',), ('stop',), ('close',)])
                else:
                    self.assertIsInstance(error, KeyboardInterrupt)
                    self.assertEqual(events, [('created',), ('motors', *speeds), ('close',)])

    def test_proportional_positions_and_adjacent_sensors(self):
        cases = [([1, 0, 0, 0, 0], (20, 80)), ([0, 1, 0, 0, 0], (35, 65)),
                 ([0, 0, 1, 0, 0], (50, 50)), ([0, 0, 0, 1, 0], (65, 35)),
                 ([0, 0, 0, 0, 1], (80, 20)), ([0, 1, 1, 0, 0], (42.5, 57.5)),
                 ([0, 0, 1, 1, 0], (57.5, 42.5))]
        for readings, speeds in cases:
            with self.subTest(readings=readings):
                events, error = self.run_controller('10_proportional_five_sensors.py', [readings])
                self.assertIsInstance(error, KeyboardInterrupt)
                self.assertEqual(events, [('created',), ('motors', *speeds), ('close',)])

    def test_proportional_stop_patterns_never_start_motors(self):
        for readings in ([0] * 5, [1] * 5):
            events, error = self.run_controller('10_proportional_five_sensors.py', [readings])
            self.assertIsNone(error)
            self.assertEqual(events, [('created',), ('stop',), ('close',)])

    def test_large_gain_clips_forward_commands(self):
        for readings, speeds in (([1, 0, 0, 0, 0], (0, 100)),
                                 ([0, 0, 0, 0, 1], (100, 0))):
            events, error = self.run_controller('10_proportional_five_sensors.py', [readings], kp=60)
            self.assertIsInstance(error, KeyboardInterrupt)
            self.assertIn(('motors', *speeds), events)
            self.assertEqual(events[-1], ('close',))

    def test_stop_after_motion_does_not_restart(self):
        for name, frames in (
            ('10_proportional_five_sensors.py', [[0, 0, 1, 0, 0], [1] * 5, [0, 0, 1, 0, 0]]),
            ('11_relay_three_sensors.py', [[0, 1, 0], [1, 1, 1], [0, 1, 0]]),
        ):
            events, error = self.run_controller(name, frames)
            self.assertIsNone(error)
            self.assertEqual(events, [('created',), ('motors', 50, 50), ('stop',), ('close',)])

    def test_initialization_and_motor_errors_close_controller(self):
        for name, readings in (('10_proportional_five_sensors.py', [0, 0, 1, 0, 0]),
                               ('11_relay_three_sensors.py', [0, 1, 0])):
            for failure in ('fail_pin', 'fail_motor'):
                events, error = self.run_controller(name, [readings], **{failure: True})
                self.assertIsNotNone(error)
                self.assertEqual(events[-1], ('close',))


if __name__ == '__main__':
    unittest.main()
