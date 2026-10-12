# RBussi Library Guide

`robot.py` is a MicroPython module for the Wemos D1 R32 robot. Copy it to `/robot.py` on the board. The module uses `machine.Pin` and `machine.PWM`, so movement programs run on the ESP32, not ordinary desktop Python.

## Create a controller

```python
from robot import RBussi

robot = RBussi()
try:
    robot.forward(speed=50, seconds=0.5)
finally:
    robot.close()
```

Create the object with `robot = RBussi()`, then call its methods. The `finally` block calls `close()` when execution ends, including after an exception or Ctrl+C. This stops the motors and releases PWM resources. Keep only one active controller. After closing it, create a new object for further movement.

First run with wheels lifted and the motor battery connected. Keep the power switch accessible. Thonny sends a local example to the selected MicroPython board when you press F5.

### Constructor options

```python
RBussi(left_reversed=False, right_reversed=False,
       left_scale=1.0, right_scale=1.0)
```

| Option | Meaning |
|---|---|
| `left_reversed` | Invert the left motor direction if its wiring differs |
| `right_reversed` | Invert the right motor direction if its wiring differs |
| `left_scale` | Multiply left PWM duty by a number from 0 to 1 |
| `right_scale` | Multiply right PWM duty by a number from 0 to 1 |

Both scales are validated before GPIO/PWM initialization. Zero disables and brakes the corresponding wheel. Corrections affect all movement methods, including reverse and turns. These settings last for this object; save them in your program to reuse them after a restart.

## Timed directional movement

| Method | Defaults | Wheel commands before scaling |
|---|---|---|
| `forward(speed=50, seconds=1)` | 50%, 1 second | `(+speed, +speed)` |
| `backward(speed=50, seconds=1)` | 50%, 1 second | `(-speed, -speed)` |
| `left(speed=50, seconds=0.3)` | 50%, 0.3 seconds | `(-speed, +speed)` |
| `right(speed=50, seconds=0.3)` | 50%, 0.3 seconds | `(+speed, -speed)` |

`speed` accepts numbers from 0 to 100. `seconds` accepts numbers from 0 to 60, including fractional seconds. Each call waits for the duration and then stops. Zero duration does not enable the motors. The left/right methods turn on the spot; duration is not an angle.

## Independent wheel commands

```python
robot = RBussi()
try:
    robot.move(left=40, right=55, seconds=0.5)
finally:
    robot.close()
```

`move(left, right, seconds=1)` accepts independent commands from −100 to 100. Positive means forward, negative means backward, and zero brakes that wheel. It waits for the duration and stops both motors in `finally`.

Examples of wheel command pairs:

| Left | Right | Intended behavior |
|---|---|---|
| 50 | 50 | Forward, subject to motor imbalance |
| -50 | -50 | Backward |
| 0 | 50 | Left wheel stopped; robot turns about that wheel |
| 50 | 0 | Right wheel stopped; robot turns about that wheel |
| -50 | 50 | Turn left on the spot |
| 50 | -50 | Turn right on the spot |
| 40 | 55 | Forward curve, normally towards the slower left side |

Actual movement depends on motor starting duty, battery, traction, and wheel balance. Begin with short tests and observe the result.

## Continuous control

`motors(left, right)` applies the same command ranges but returns without waiting or scheduling a stop. Commands remain active until changed, stopped, or the controller is closed.

```python
from robot import RBussi
from time import sleep_ms

robot = RBussi()
try:
    robot.motors(left=40, right=55)
    sleep_ms(300)
    robot.motors(left=55, right=40)
    sleep_ms(300)
    robot.stop()
finally:
    robot.close()
```

Use this method later in a line-following loop: read sensors, calculate wheel commands, and update `motors()` repeatedly. The present library provides motor control only; a calibrated line-sensor API is not included yet.

## Stop and cleanup

- `stop()` sets both PWM duties to zero and engages both brakes. It does not release PWM; the same object can move again.
- `close()` stops the motors, deinitializes PWM, and leaves enable pins low. Repeated `stop()` or `close()` calls are allowed.
- `motors()` on a closed object raises `RuntimeError`.
- Before reversing a moving wheel, the driver stops both wheels and waits 20 ms.
- Invalid wheel speeds raise `ValueError` and stop existing movement. Timed commands stop even when validation fails or execution is interrupted.

These are program-level stopping measures. A board reset, stalled program, disconnected host, or electrical fault is not covered by a separate hardware emergency-stop mechanism. Keep motor power accessible during tests.

## Calibration and limits

Speed arguments are PWM duty percentages, not measured wheel velocities. There are no wheel encoders, so this API cannot command a measured distance or exact turn angle. Start with equal scales, then reduce the faster wheel's scale using the [calibration procedure](wheel-calibration.md).

For example, `left_scale=0.95` with a left command of 50 produces 47.5% left PWM duty. The value is illustrative; select settings for each robot. Battery voltage, surface, speed, and direction can change the balance.

## Examples

Run one example at a time from Thonny after uploading the library:

| File | Purpose |
|---|---|
| [00_check_setup.py](../examples/00_check_setup.py) | Import and initialization with no movement |
| [first_drive.py](../examples/first_drive.py) | Short forward movement |
| [01_variables.py](../examples/01_variables.py) | Change speed and duration variables |
| [02_sequence.py](../examples/02_sequence.py) | Movement sequence with a pause |
| [03_wheel_balance.py](../examples/03_wheel_balance.py) | Per-robot scale settings |
| [04_wheel_control.py](../examples/04_wheel_control.py) | Independent timed wheel commands |
| [05_continuous_control.py](../examples/05_continuous_control.py) | Update continuous commands and stop |
| [stop.py](../examples/stop.py) | Request a motor stop |

Preparation status: default forward motion was physically observed. Reverse, turns, the new scale correction, and the additional wheel-control examples require physical verification before classroom use. Host tests use simulated GPIO/PWM and do not establish physical motion accuracy.
