# Day 2 — Sensor and Control Observations

Name: __________ Robot ID: __________ Date: __________

## Sensor trimmer check

Sensing height: __________ Supply voltage: __________ D0 high voltage: __________

| Sensor | Header / GPIO | White level (0/1) | Black level (0/1) |
|---|---|---|---|
| Left | | | |
| Right | | | |

What happened when only the left sensor was covered? __________

Where did you see the readings: Shell, Plotter, LED? __________

## External LED

GPIO: __________ Series resistor: __________

Mark the anode and cathode in your wiring sketch. Why is the resistor needed? __________

Adjust the module trimmers for stable readings. The instructor confirmed white = 0 and black = 1; the examples use these levels directly. No software calibration or settings module is needed.

## Reactive movement

Black command: __________ White command: __________

Which line reads the sensor? __________ Which line makes the decision? __________

## Stop at the bar

Left black only: __________ Both black: __________

Did the robot stop because of the bar or Ctrl+C? __________

What would change if `and` became `or`? __________

## Two-sensor controller

Track: narrow black stripe on white, between sensor spots when centred.

| Left | Right | Predicted command | Observed wheel response |
|---|---|---|---|
| White | White | | |
| Black | White | | |
| White | Black | | |
| Black | Black | | |

Wheel scales: left __________ right __________

Optional floor test: base PWM __________ inner PWM __________ duration __________

| Trial | Completed test section? | What happened? |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

Why do two white readings fail to prove that the line is still between the sensors? __________

## Remote laboratory

Task completed: __________ Local D0 range: __________ Remote sensor range: __________

One difference between the local and remote sensors: __________

Saved program filename: __________ One question for Day 3: __________
