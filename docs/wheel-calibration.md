# Wheel Speed and Straight-Line Calibration

The local robot has no wheel encoders. Speed arguments specify PWM duty, not measured wheel speed or travel distance. Identical commands can produce different wheel speeds.

## Independent wheel commands

```python
from robot import RBussi

with RBussi() as robot:
    robot.move(left=45, right=50, seconds=0.5)
```

`move()` stops after the specified duration. For line following, `motors(left, right)` updates the two commands continuously; use a `with` block or `try/finally` to stop on exit.

## Per-robot correction

`left_scale` and `right_scale` multiply the requested PWM duty for each wheel. Both default to 1.0 and accept values from 0.0 to 1.0. Zero disables and brakes that wheel. Corrections apply to all movement methods, including reverse and turns. Direction-inversion settings are independent of these corrections.

Example only: if the left wheel is faster, try reducing its command:

```python
from robot import RBussi

with RBussi(left_scale=0.95, right_scale=1.0) as robot:
    robot.forward(speed=50, seconds=0.5)
```

Here the left PWM duty is 47.5% and the right duty is 50%. Neither value is a measured velocity. The value 0.95 is illustrative, not a calibration measured on your robot.

## Day 1 activity: 10–15 minutes

1. Verify both wheel directions with wheels lifted. Check batteries, wheel mounting, and drag before adjusting software.
2. Place the robot in the marked lane. Use the same starting pose, surface, battery, speed (50), and duration (initially 0.5 seconds). Keep the USB cable slack and clear of wheels.
3. Run `examples/03_wheel_balance.py` with both scales at 1.0. Record drift over several short trials.
4. A consistent curve to the right usually means the left wheel is moving faster; reduce `LEFT_SCALE`. For a curve to the left, reduce `RIGHT_SCALE`. First rule out cable pull, slipping, or mechanical obstruction.
5. Reduce only the faster wheel's scale in steps of 0.05, then refine if useful. Keep the other scale at 1.0. Compare at least three trials before deciding.
6. Save the chosen values in your own program and worksheet, together with the robot ID and test conditions. Constructor values are not saved automatically on the board.

Do not increase duration beyond the available floor area or USB cable slack. Keep the power switch accessible. Stop if the slower wheel cannot turn reliably; excessive reduction can put a motor below its starting duty.

## What calibration does and does not provide

A fixed correction can reduce repeatable drift around the tested operating point. It cannot guarantee straight motion or exact distances and angles. Battery voltage, surface, load, motor starting thresholds, and direction can change the balance. Retest at the speeds used later; a correction for forward travel may not suit reverse or an on-the-spot turn.

During line following, sensor feedback adjusts the left and right commands repeatedly. Keep wheel scales as the initial balance correction, then tune the controller using the corrected robot. Line sensors provide feedback about the path, not individual wheel velocity.

This update has host tests with simulated GPIO/PWM. Its calibration behavior still needs verification on the physical robots.
