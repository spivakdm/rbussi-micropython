# Day 2 — Sensor and LED Exercises

Complete programs for the instructor and students. Run one at a time in Thonny with MicroPython (ESP32). These are digital D0 examples, not analog ADC examples. See the [teaching plan](../../docs/day-02-plan.md) and [slide outline](../../docs/day-02-slides.md).

## Before running

1. Keep `/robot.py` on the ESP32. No additional library or settings file is needed.
2. Keep motor power off for exercises 01–05 and 07. Check sensor supply and D0 voltage before connecting to ESP32.
3. Open an exercise on your computer and press F5. It declares its own pins and parameters at the top; the exercise need not be saved on the board.
4. Use the sensor trimmers to set a reliable black/white response. Run 01 to check it. The instructor confirmed white = 0 and black = 1; the BLACK constants are defined as 1 directly in the examples. No software calibration is required.
5. Run 06, 08 and 09 with wheels lifted first and the motor battery connected. Copy any wheel-scale correction into the local `LEFT_SCALE`/`RIGHT_SCALE` constants. The movement limit is five seconds for 06/08 and one second for 09; Ctrl+C requests software cleanup.

GPIO assignments initially follow the drawing, left A3/GPIO34 and right A2/GPIO35. Verify the sides physically. An old settings file left on the board is ignored by these examples.

| File | Exercise | Expected result |
|---|---|---|
| `01_read_sensors.py` | Connect and measure D0 | Two numeric columns in Shell for 15 s; optional View > Plotter |
| `02_builtin_led.py` | Digital output | GPIO2 LED blinks five times |
| `03_sensor_builtin_led.py` | Compare a reading with the measured black level | Right sensor on black turns the built-in LED on, for 15 s |
| `04_external_led.py` | Breadboard LED and series resistor | GPIO26/D2 LED blinks five times |
| `05_sensor_external_led.py` | Sensor-driven external output | Right sensor on black turns the external LED on, for 15 s |
| `06_black_forward_white_backward.py` | `if` and continuous motor commands | Right sensor black: forward; white: backward, for at most 5 s |
| `07_two_sensor_states.py` | Four combinations and `if/elif/else` | Prints colour names and intended actions, without movement |
| `08_relay_line_follower.py` | Repeated read–decide–act | Follows a narrow black stripe between the sensors; bounded 5 s trial |
| `09_stop_at_bar.py` | Logical `and` and `break` | Drives straight until both sensors see black, or at most 1 s |

## Stop at the bar

Adjust both sensor trimmers and check black/white readings first. Run `09_stop_at_bar.py` with wheels lifted; move the [printed stop bar](../../printables/README.md) beneath both sensors. Both-black stops and ends the run; a single black sensor does not stop it. If both are already black at launch, no forward command is issued. Without detection it stops after the local `MAX_RUN_MS = 1000` limit. The script does not restart automatically and does not steer. For a floor trial, point it towards the bar from a short distance and check the actual available space.

## Wiring

Sensors: approved supply to VCC, common GND, left D0 to A3, right D0 to A2. A sensor's D0 terminal is not Wemos D0/GPIO3. Output high must be compatible with ESP32 3.3 V GPIO. Module supply is not inferred from terminal labels.

External standard LED: GPIO26/D2 → 470-ohm resistor → anode (+), cathode (-) → GND. Confirm this contact is free on the actual motor shield. Switch all power off to rewire.

## Relay track assumptions

The track is black on white. When centred, both sensor spots see white and the stripe lies between them. Left black causes left steering, right black causes right steering, and both black stops and ends the run. Both white also occurs after losing the stripe completely, so this example cannot guarantee line-loss detection. Test on a short, clear course with wide curves.

Remote-lab exercises use the remote course's supplied code, not these GPIO assignments or `RBussi`.

Status: host logic and cleanup checks only; actual sensor electrical compatibility, trimmer adjustment and robot tracking require physical rehearsal.

## Run without the USB cable

In Thonny, save the selected complete exercise to **MicroPython device** as `/main.py`. Keep `/robot.py` on the board too; Day 2 needs no extra settings module. Reset or power-cycle the ESP32 to start the program automatically. Use `main.py` for the application, not `boot.py`, which is for early startup configuration.

The external supply must power the ESP32 as well as the motor driver. Disconnecting USB does not necessarily reset the board or start a new run. The movement examples end after their time limits and will run again after a reset. Keep the wheels lifted for the first startup test.
