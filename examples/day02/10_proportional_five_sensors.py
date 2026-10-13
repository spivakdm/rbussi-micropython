"""Extra task: five digital sensors and proportional steering using for.

Requires FIVE connected sensors, in physical left-to-right order below.
Proposed extra wiring; the prepared robot originally has only two sensors.
Black = 1, white = 0. Start with the line under the centre sensor.
No timer. All-white or all-black ends the run; Ctrl+C requests cleanup.
Assumes a single contiguous stripe, not junctions or multiple lines.
"""
from machine import Pin
from time import sleep_ms
from robot import RBussi

# Outer left, inner left, centre, inner right, outer right.
SENSOR_GPIOS = [39, 34, 36, 35, 4]  # A5, A3, A4, A2, A1; proposed wiring.
POSITIONS = [-2, -1, 0, 1, 2]
BASE_SPEED = 50
KP = 15
LEFT_SCALE = 1.0
RIGHT_SCALE = 1.0
SAMPLE_MS = 20

robot = RBussi(left_scale=LEFT_SCALE, right_scale=RIGHT_SCALE)
try:
    sensors = []
    for gpio in SENSOR_GPIOS:
        sensors.append(Pin(gpio, Pin.IN))

    while True:
        total = 0
        count = 0
        for i in range(len(sensors)):
            reading = sensors[i].value()
            total += POSITIONS[i] * reading
            count += reading

        if count == 0:
            robot.stop()
            print('No sensor sees black: stopped')
            break
        elif count == len(sensors):
            robot.stop()
            print('All sensors see black: stopped')
            break
        else:
            error = total / count
            correction = KP * error
            # Forward-only wheel commands, limited to 0..100% PWM.
            left_speed = max(0, min(100, BASE_SPEED + correction))
            right_speed = max(0, min(100, BASE_SPEED - correction))
            robot.motors(left=left_speed, right=right_speed)
            # Optional bench telemetry:
            # print(count, error, left_speed, right_speed)

        sleep_ms(SAMPLE_MS)
finally:
    robot.close()
