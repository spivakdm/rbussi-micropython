# Extra Tasks — Line Control with More Sensors

Metropolia ICT Summer School · Introduction to Mobile Robotics with a Remote Laboratory.

Two optional extensions to the two-sensor lesson. All sensors below have digital D0 outputs: **white = 0, black = 1**. Thresholds are set with the module trimmers, with no software calibration or extra settings module.

Work through the prediction tables before running the reference solutions. If only the original two sensors are available, complete the logic and arithmetic with paper readings or a Python list on the computer. Physical tests require three or five connected sensors respectively. Do not run the physical programs with missing sensors: an unconnected input can return meaningless levels.

## Hardware and track

The existing kit has left A3/GPIO34 and right A2/GPIO35. The extra wiring below is a **proposal**, not a record of connections already made. Confirm the accessible headers and physical sensor order on the actual kit. Motor pins remain unchanged.

| Physical position | Three-sensor version | Five-sensor version |
|---|---|---|
| Outer left | - | A5 / GPIO39, added sensor |
| Left / inner left | A3 / GPIO34, existing sensor | A3 / GPIO34, existing sensor |
| Centre | A4 / GPIO36, added sensor | A4 / GPIO36, added sensor |
| Right / inner right | A2 / GPIO35, existing sensor | A2 / GPIO35, existing sensor |
| Outer right | - | A1 / GPIO4, added sensor |

Connect each module's D0 to its assigned input and use a common ground. Verify module supply and 3.3 V-compatible output levels as in the [wiring guide](wiring-reference.md). GPIO34–39 are input-only and have no internal pull resistors; do not leave them floating or rely on internal pull-ups.

Use a single black stripe on white. When centred, the stripe must pass beneath the **centre sensor**. This differs from the earlier two-sensor geometry, where the stripe sat between the two sensor spots. Match sensor spacing and stripe width so adjacent states are detectable without gaps in coverage. Use roughly equal physical spacing for the five-sensor weights below.

Only `robot.py` is required on the ESP32. Open the selected complete example on the computer and run it with F5. Each program has local pin constants, `while True` and `finally: robot.close()`. There is no timer. Start with wheels lifted and move paper beneath the sensors. Ctrl+C requests cleanup; without USB, use motor power to stop an unintended run.

## Task A — Five sensors and proportional steering

Goal: calculate a position estimate with a `for` loop and turn in proportion to the error.

Reference: [10_proportional_five_sensors.py](../examples/day02/10_proportional_five_sensors.py).

### A1. Predict the position

Positions from left to right:

```python
positions = [-2, -1, 0, 1, 2]
```

A black reading contributes that sensor's position. A white reading contributes zero. Divide the sum by the number of black readings:

```python
readings = [0, 1, 1, 0, 0]
positions = [-2, -1, 0, 1, 2]

total = 0
count = 0
for i in range(len(readings)):
    total += positions[i] * readings[i]
    count += readings[i]

if count == 0:
    print('No sensor sees the line')
elif count == len(readings):
    print('Broad black marker')
else:
    error = total / count
    print('Error:', error)
```

This calculation-only snippet runs on ordinary desktop Python too. For the given readings: `total = -1`, `count = 2`, so `error = -0.5`.

**Error is the estimated line position, not Kp.** Negative means left, zero means centre and positive means right. It is expressed in sensor-spacing units, not centimetres.

### A2. Calculate the wheel commands

Use `BASE_SPEED = 50` and `KP = 15`:

```python
correction = KP * error
left_speed = BASE_SPEED + correction
right_speed = BASE_SPEED - correction
```

Limit both commands to 0–100 for this forward-only exercise. This example deliberately brakes a wheel rather than requesting negative PWM when the correction is large.

| Readings, left to right | Count | Error | Left PWM | Right PWM |
|---|---|---|---|---|
| `10000` | | | | |
| `01000` | | | | |
| `00100` | | | | |
| `00010` | | | | |
| `00001` | | | | |
| `01100` | | | | |
| `00110` | | | | |
| `00000` | | | Stop | Stop |
| `11111` | | | Stop | Stop |

Instructor checks: `10000` gives −2 and 20/80; `00100` gives 0 and 50/50; `01100` gives −0.5 and 42.5/57.5; `00110` gives +0.5 and 57.5/42.5.

### A3. Test and compare

1. Check raw levels and the physical left-to-right ordering with motors off.
2. With wheels lifted, place the line beneath each sensor and compare wheel commands with your table.
3. Check all-white and all-black: both must stop and end the run without division by zero.
4. Test `KP = 10`, `15` and `20` at the same base PWM. Record oscillation, missed turns and successful runs on the same course. Then change base PWM while keeping Kp fixed.
5. Explain why a larger Kp means a stronger correction, not automatically a better or faster robot.

The reference estimates the centre of the black readings. It assumes one contiguous stripe under the sensor row. A pattern such as `10001` also averages to zero, even though the middle sensor sees white; junctions, multiple lines and gaps in coverage need separate rules. An optional extension is to stop on noncontiguous black patterns.

Completion: working `for` calculation, correct steering sign, bounded wheel commands and an explanation of one sensor-array limitation.

## Task B — Three sensors and relay steering

Goal: use explicit `if/elif/else` decisions with gentle and strong corrections. No weighted-average formula is needed.

Reference: [11_relay_three_sensors.py](../examples/day02/11_relay_three_sensors.py).

Use `SPEED = 50`, `SLOW_SPEED = 30`, `INNER_SPEED = 0`:

| Left | Centre | Right | Action | Left PWM | Right PWM |
|---|---|---|---|---|---|
| 0 | 1 | 0 | Forward | 50 | 50 |
| 1 | 1 | 0 | Gentle left | 30 | 50 |
| 1 | 0 | 0 | Strong left | 0 | 50 |
| 0 | 1 | 1 | Gentle right | 50 | 30 |
| 0 | 0 | 1 | Strong right | 50 | 0 |
| 0 | 0 | 0 | No black detected: stop | 0 | 0 |
| 1 | 1 | 1 | Broad black marker: stop | 0 | 0 |
| 1 | 0 | 1 | Ambiguous pattern: stop | 0 | 0 |

For example:

```python
if not left_black and centre_black and not right_black:
    robot.motors(left=50, right=50)
elif left_black and centre_black and not right_black:
    robot.motors(left=30, right=50)
```

1. Write the other conditions before opening the full solution.
2. With wheels lifted, check all eight patterns using paper and confirm that the stop patterns end the program.
3. Compare `SLOW_SPEED = 20`, `30` and `40` at fixed base PWM. Explain the difference between gentle and strong correction.
4. Test a short course and record whether the controller oscillates or loses the stripe. Raise speed only after a repeatable baseline run.

Completion: correct eight-state behavior, both directions of correction, and stopping for each unsupported state.

## Compare the approaches

- Three-sensor relay chooses a command from a small table.
- Five-sensor P control calculates command differences from an estimated error.
- More sensors provide information; a higher speed still depends on placement, sample interval, motor response and the track.
- Neither example measures wheel velocity or distance. Keep per-robot `LEFT_SCALE` / `RIGHT_SCALE` if needed.

Suggested teaching order: three-sensor relay first, then five-sensor position arithmetic and P steering. These are optional extensions, not additional mandatory work inside the existing four-hour Day 2 schedule.

## Sources and preparation status

[Wemos D1 R32 header/GPIO mapping](https://github.com/UCLM-ESI/wemos-d1-r32-pio/blob/master/pins_arduino.h). The additional wiring above has not been physically tested.

[Pololu sensor-array usage and position-based steering](https://github.com/pololu/qtr-sensors-arduino/blob/master/usage.md) illustrates the general position/error approach. Our examples use digital D0 readings and MicroPython, not Pololu's library or its analog calibration API.

Host tests check the eight relay states, P-command arithmetic, clipping, stop patterns and cleanup on interruption. They do not verify hardware wiring, sensor response or physical tracking speed.
