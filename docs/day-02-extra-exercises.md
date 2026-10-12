# Additional Digital Line-Sensor Exercises

Choose one or two extensions for Day 2; keep the main [lesson plan](day-02-plan.md) within 13:00–17:00. The existing sensor outputs are digital D0, so the experiments observe 0/1 transitions, not continuous reflectance.

Use the [A4 print template](../printables/README.md) for calibration and short sections. Most initial experiments work with motor power off or the robot lifted while paper moves beneath the sensors.

| Exercise | Student task | Python / robotics concept | Completion evidence |
|---|---|---|---|
| Guess the readings | Predict both sensor colours for four paper positions, then check Shell | Booleans, independent channels, interpreting measurements | Four correct predictions after polarity calibration |
| Sensor-height experiment | Repeat white/black measurements at several recorded heights around the working position | Controlled experiments and calibration | A table of reliable and unreliable responses |
| Count line crossings | Move the narrow stripe across one stationary sensor several times; count only white-to-black transitions | Previous state, `if`, counters, edge detection | Holding black under the sensor increments only once |
| Stop at the bar | Move the broad stop bar under both sensors, then try a brief forward trial towards it | `and`, `break`, a chosen marker rule | Both-black stops and ends the run |
| Detect changes only | Print a message only when either sensor changes | Tuples, previous state, reducing telemetry | No repeated messages while the surface stays unchanged |
| Stabilise a flickering edge | Require three consecutive equal samples before accepting a new state | Debouncing, counters, response delay | Compare raw transitions and accepted transitions |
| Tune relay steering | Compare inner-wheel PWM 0 with a higher value at fixed base PWM | Controlled parameter changes and feedback | A repeatable short trial and observations for each setting |
| Change the sample period | Compare 20 ms and 100 ms at fixed duty on a suitably long course | Sampling interval and feedback response | Explain what changed and what stayed constant |

## Suggested priorities

For students new to Python, choose **count line crossings**: the visible difference between a level and a transition makes state variables useful. Start with a single sensor and move paper manually.

For the robotics goal, choose **stop at the bar**, then **tune relay steering**. Use `09_stop_at_bar.py` for a separate straight-driving marker exercise. The existing `08_relay_line_follower.py` also stops on both-black while steering along the stripe.

For faster students, combine **detect changes only** with **debouncing**. Require them to explain the trade-off: accepted readings become more stable, but a new state takes longer to affect the robot.

A two-D0 system cannot determine how far the stripe is from the robot or distinguish centred white/white from some lost-line situations. Do not describe raw 0/1 values as a continuous position error. Use the remote Octoliner for later proportional-control comparisons.
