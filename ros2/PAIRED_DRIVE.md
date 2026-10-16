# Move the real RBussi and simulator together

This is **command mirroring**, not position tracking. The simulator illustrates
requested motion; it does not measure the real robot. PWM and simulator velocity
have different units. Wheel slip, battery level and motor differences cause drift.

Use classroom image **0.2.8**. Download and load the matching AMD64 or ARM64
archive as described in [README.md](README.md), then run:

```sh
docker compose up -d
```

The normal compose file includes the feature; no extra override or local build is
needed. `compose.paired.yaml` remains a compatible optional alias for the same
image. Starting the desktop never starts paired driving automatically.

When upgrading, save open editor files first: replacing the container closes its
terminals. Copy your private `settings.env` and any student work into the new kit.
No board firmware update is needed when the prepared ROS/MQTT files are installed.

## Before moving

Use the prepared ROS/MQTT firmware in `robot/`, including `robot_mqtt.py` and
`drive_command.py`. It limits the duration of each motor request on the ESP32.
No new firmware is required if these files are already installed.
Set your own `ROBOT_NAME`, MQTT account and prefix in `settings.env`.
Lift the wheels for the first test. Keep the motor power switch accessible.
Stop the line follower, `sim-line-track`, `sim-line-demo`, ordinary teleop and any other motor
controller. Do not run two independent programs that command the same robot.

## Three browser terminals

Terminal A — connect the real robot:

```sh
robot-connect
```

Terminal B — start the translator and real sensor display:

```sh
paired-drive
```

Wait for `Ready for new commands`. The simulator now shows a **Real sensors**
label at the bottom. It reads actual `/robotNN/line` values, not virtual sensors.
`no fresh data` means readings are missing or more than one second old.

Terminal C — keyboard control (open with F8):

```sh
paired-teleop
```

Hold **W** forward, **S** backward, **A** turn left, **D** turn right.
**Space** stops; **Q** or **Ctrl+C** exits. Keep keyboard focus in this terminal.
Keyboard auto-repeat drives repeated commands. Releasing a key stops sending
nonzero speed after 0.25 seconds; the initial keyboard repeat delay can cause a
short pause at the start of a held key.

## ROS message paths

```text
paired_keyboard -> /paired/cmd_vel (Twist) -> paired_drive
                                               |       |
                         /turtle1/cmd_vel <-----+       +----> /robot01/wheels (String)
                                  |                              |
                              turtlesim                      mqtt_bridge
                                                                 |
                                                              MQTT -> ESP32
```

Replace `robot01` with the account selected in `settings.env`. The node uses that
name automatically. Ordinary `/turtle1/cmd_vel` messages remain simulator-only.
Paired driving is never started automatically with the desktop.

For a terminal command, stop keyboard control first:

```sh
ros2 topic pub --rate 10 /paired/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.8}, angular: {z: 0.0}}"
```

Ctrl+C stops this stream. A repeated command keeps moving until stopped; begin
with wheels lifted. Do not use `--once` for a long movement: the input watchdog
expires after 0.4 seconds.

## Speeds and stopping

`linear.x` requests forward speed; `angular.z` requests turn rate. Positive turn
means left. The teaching conversion is:

```text
left PWM  = 35 * forward - 20 * turn
right PWM = 35 * forward + 20 * turn
```

Inputs are limited to ±1.0 forward and ±1.5 turn; wheel PWM is scaled together to
stay within ±40%. These are approximate teaching gains, not calibrated odometry.
Low PWM may not overcome friction on the floor.

- Commands refresh at 10 Hz; each ESP32 wheel request expires after 300 ms.
- Missing input for 0.4 s sends zero speed to both outputs.
- Missing real state telemetry for 1 s stops paired output and discards old input.
- Another publisher on `/turtle1/cmd_vel` blocks paired motion.
- After recovery, a new input command is required.
- Killing the translator cannot send an explicit stop; the ESP32 command lease
  and Turtlesim command timeout still stop motion independently.

Network latency and ESP32 loop timing add delay. This is a classroom demonstration,
not a safety-rated emergency stop. Use the physical motor switch when needed.

## Read real sensors and map colour

```sh
ros2 topic echo /robot01/line
ros2 topic echo /robot01/state
ros2 topic echo /turtle1/color_sensor
```

Real line sensors: `[left, right]`, white 0, black 1. `/sim/line` remains the separate
virtual two-sensor model. The colour sensor reads the original map under the
simulated robot's centre; it ignores robot sprites, pen trails and teaching
line/sensor overlays. Resizing the window does not change the sampled map position.

## End

Quit keyboard control, stop `paired-drive`, then stop `robot-connect`. Switch motor
power off. An independently powered ESP32 continues waiting for MQTT commands.
