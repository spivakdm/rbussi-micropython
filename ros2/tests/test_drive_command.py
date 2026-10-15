import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'robot'))
from drive_command import parse_drive


class DriveTests(unittest.TestCase):
    def test_directions_and_stop(self):
        self.assertEqual(parse_drive('move', b'forward'), (40, 40, 1000))
        self.assertEqual(parse_drive('move', b'backward'), (-40, -40, 1000))
        self.assertEqual(parse_drive('move', b'left'), (-35, 35, 400))
        self.assertEqual(parse_drive('move', b'right'), (35, -35, 400))
        self.assertEqual(parse_drive('move', b'stop'), (0, 0, 0))

    def test_wheels(self):
        self.assertEqual(parse_drive('wheels', b'{"left":30,"right":-20,"duration_ms":500}'), (30, -20, 500))

    def test_invalid_commands(self):
        for payload in [b'{}', b'[]', b'null', b'bad',
                        b'{"left":true,"right":0,"duration_ms":500}',
                        b'{"left":61,"right":0,"duration_ms":500}',
                        b'{"left":0,"right":0,"duration_ms":1001}',
                        b'{"left":0,"right":0,"duration_ms":-1}']:
            with self.subTest(payload=payload), self.assertRaises((ValueError, KeyError, TypeError)):
                parse_drive('wheels', payload)
        with self.assertRaises(ValueError):
            parse_drive('move', b'FORWARD')


if __name__ == '__main__':
    unittest.main()
