# RBussi — Movement Quick Reference

Copy `robot.py` to the MicroPython board. Run your own program from Thonny with MicroPython (ESP32) selected.

```python
from robot import RBussi

with RBussi() as robot:
    robot.forward(speed=50, seconds=0.5)
```

| Command | Action |
|---|---|
| `forward(speed=50, seconds=1)` | Forward, then stop |
| `backward(speed=50, seconds=1)` | Backward, then stop |
| `left(speed=50, seconds=0.3)` | Turn left on the spot, then stop |
| `right(speed=50, seconds=0.3)` | Turn right on the spot, then stop |
| `move(left=40, right=60, seconds=1)` | Independent wheel speeds for a fixed duration |
| `motors(left=40, right=60)` | Continuous motion until another command or stop |
| `stop()` | Stop both motors |
| `close()` | Stop and release PWM; called when leaving `with` |

Directional speed: 0–100%. Independent wheel speeds: −100 to 100%, positive means forward. Duration: 0–60 seconds. Zero duration does not start the motors. Speed is PWM duty, not measured velocity; turn duration is not an angle.

Keep a single active `RBussi` object. Use the `with` pattern, especially for continuous motion. Timed commands stop in `finally`, including on interruption. Keep the motor-power switch accessible for unexpected behavior.

Right wheel: A. Left wheel: B. If a particular robot's motor wiring differs, ask the instructor about `RBussi(left_reversed=True)` or `RBussi(right_reversed=True)`.

For unequal motors, use `RBussi(left_scale=0.95, right_scale=1.0)` as an example of reducing the left wheel's PWM duty. Both scales accept 0–1 and default to 1; choose values experimentally for each robot. They affect every movement command. See [wheel calibration](wheel-calibration.md). Without encoders, this is a fixed correction, not measured speed control.

First test: wheels lifted, battery connected, short duration. Save your script on the computer under your own filename. Do not use `robot.py` for a student script or `main.py` for a Day 1 movement program.
