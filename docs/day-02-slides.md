# Day 2 Presentation Outline — Sense, Decide, Act

English slide copy for a concise Day 2 deck. Keep the existing light background, dark text and Metropolia logo in the upper right. Each slide introduces one practical step; put setup details and recovery instructions in the handout. This file is a storyboard, not a finished PPTX.

Teaching plan: [day-02-plan.md](day-02-plan.md). Runnable instructor examples: [examples/day02](../examples/day02/README.md).

## 1. From Sensors to Decisions

Day 2 · Tuesday 13 October 2026 · 13:00–17:00

Read a surface. Show a result. Change the robot's motion.

Instructor note: recap Day 1 movement and GPIO/PWM briefly. Show a sensor-driven LED before explaining its code.

## 2. Today

- Connect and read the sensors.
- Control built-in and external LEDs.
- Make movement depend on colour.
- Try two-sensor steering and the remote laboratory.

Instructor note: 13:10 sensors, 14:00 built-in LED, 14:30 external LED, 14:55 reactive movement, 15:35 two sensors, 16:15 remote laboratory. Breaks 14:15 and 15:20.

## 3. Connect a Digital Line Sensor

VCC: check the module's supply requirements
GND: common ground
D0: digital signal to A2 or A3

A2 = GPIO35 · A3 = GPIO34

Instructor note: use the existing instructor wiring picture and board pinout. Do not add an unverified 5 V supply instruction. Confirm D0 high voltage is compatible with ESP32. Sensor D0 is not Wemos D0. Expected side mapping is right A2, left A3; verify by covering each sensor.

## 4. Read It in Thonny

```python
sensor = Pin(35, Pin.IN)
print(sensor.value())
```

Shell shows 0 or 1.
View > Plotter shows changes over time.

Exercise: `01_read_sensors.py`.

Instructor note: ESP32 sends `print()` through the USB serial connection to Thonny. Introduce imports and a short delayed loop with the full example. No separate serial monitor. D0 is a comparator output, so no ADC is needed.

## 5. Measure Before Deciding

Test white and black under each sensor.
Record the four levels in `day02_settings.py`.
Upload the settings file again.

Instructor note: white is not universally 0 and black is not universally 1. Check sensor height and threshold adjustment. Show the calibration table from the worksheet. Explain `raw == RIGHT_BLACK` only after measuring polarity.

## 6. The Built-in LED

```python
led = Pin(2, Pin.OUT)
led.on()
led.off()
```

Exercise: blink five times.

Instructor note: run `02_builtin_led.py`. GPIO2 is the programmable LED, separate from the power indicator. Explain high/low and a delay.

## 7. Show What the Sensor Sees

```python
black = sensor.value() == RIGHT_BLACK
led.value(black)
```

Black: LED on. White: LED off.

Exercise: `03_sensor_builtin_led.py`.

Instructor note: the snippet is conceptual; use the complete file with calibrated settings. Ask students to predict the result before changing the comparison.

## 8. An External LED

```text
D2 / GPIO26 --- 470 ohm --- LED (+)
                           LED (-) --- GND
```

Power off before wiring.
Blink first, then add the sensor.

Exercises: `04_external_led.py`, `05_sensor_external_led.py`.

Instructor note: use a photo of the actual assembled breadboard in the eventual deck, or this simple wiring notation. Explain series resistance and polarity. Confirm GPIO26 is free on the shield. Do not use GPIO34/35 as LED outputs.

## 9. A Sensor Changes Movement

```python
if raw == RIGHT_BLACK:
    robot.motors(left=50, right=50)
else:
    robot.motors(left=-50, right=-50)
```

Black: forward. White: backward.
Wheels lifted. Five-second trial.

Exercise: `06_black_forward_white_backward.py`.

Instructor note: full example handles timeout and cleanup. This is reactive movement, not a line follower. Use paper rather than hands near wheels.

## 10. Stop at the Black Bar

```python
if left_black and right_black:
    robot.stop()
    break
```

Both sensors black: stop and end the run.

Exercise: `09_stop_at_bar.py`.

Instructor note: use the full program, which reads both sensors before starting forward motion. It drives straight, does not steer, and stops after at most one second even if no bar is detected. First move the paper under the lifted robot. Ask students to predict the difference between `and` and `or`. For a floor test, start close to the broad printed bar.

## 11. Two Sensors See Four States

Read left and right together.
Predict a command before running motors.

Exercise: `07_two_sensor_states.py`.

Instructor note: use black/white cards to demonstrate all four combinations with motor power off. Use colour names after calibration, rather than attaching universal meanings to 0 and 1.

## 12. Relay Steering

Narrow black line on white, between the sensors.

| Left | Right | Action |
|---|---|---|
| White | White | Forward |
| Black | White | Steer left |
| White | Black | Steer right |
| Black | Black | Stop |

Instructor note: show the actual track and sensor spacing. This table is not for a white stripe. Stopping on both-black is the chosen exercise behavior.

## 13. Read, Decide, Act Again

Read both sensors.
Choose one of the four actions.
Update wheel commands and repeat.

Exercise: `08_relay_line_follower.py`.

Two white readings can also mean the line is missing.

Instructor note: first test wheel responses with the robot lifted, then a five-second floor trial centred on the stripe. Compare `INNER_SPEED = 0` with a higher value. Mention that the loop has a time limit, but no reliable line-loss detector.

## 14. The Remote Laboratory

Task 10: read the Octoliner.
Task 11: stop at a detected line.
If ready: task 12 or LED telemetry in task 14.

Compare two binary sensors with an eight-channel array.

Instructor note: use the course's actual API, Moodle/LTI links and templates. Simulate supported tasks while waiting. Check unlock rules. Leave task 13 and remote line following for Day 3 unless progress allows more.

## 15. Today's Checkpoint

I can read and explain sensor values.
My sensor controls an LED or the motors.
I saved my code and calibration.
I can explain one limitation of two sensors.

Instructor note: collect the worksheet and ask each student to point to the read, decision and output parts of their program. Relay following is a stretch outcome. Next: improve tracking and compare with the remote robot.
