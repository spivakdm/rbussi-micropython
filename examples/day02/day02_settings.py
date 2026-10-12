"""Per-robot settings. Upload this file to /day02_settings.py on the ESP32.

Read raw values with 01_read_sensors.py before filling the four levels.
A2/A3 are header positions; sensor D0 is a digital output, not ESP32 GPIO0.
"""
LEFT_GPIO = 34   # A3; verify by covering only the left sensor.
RIGHT_GPIO = 35  # A2; verify by covering only the right sensor.
BUILTIN_LED_GPIO = 2
EXTERNAL_LED_GPIO = 26  # D2; confirm the shield leaves this contact free.

LEFT_WHITE = None
LEFT_BLACK = None
RIGHT_WHITE = None
RIGHT_BLACK = None

LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0
SPEED = 50
INNER_SPEED = 0  # Brake the inner wheel for a strong steering correction.
RUN_MS = 5000    # Bounded movement trial, not an independent emergency stop.
SAMPLE_MS = 20


def require_calibration():
    """Reject missing or indistinguishable digital colour measurements."""
    for side, white, black in (
        ('left', LEFT_WHITE, LEFT_BLACK),
        ('right', RIGHT_WHITE, RIGHT_BLACK),
    ):
        if white not in (0, 1) or black not in (0, 1) or white == black:
            raise ValueError('Set distinct 0/1 WHITE and BLACK levels for ' + side
                             + ' in day02_settings.py, then upload it again')
