# Instructor plan: virtual RBussi first, real RBussi next

**Audience:** robotics beginners, including students with no programming experience.
**Session:** 13:00–17:00.
**Materials:** [setup](README.md), [Turtlesim exercises](SIMULATOR.md), [physical-robot exercises](EXERCISES.md), [kit 0.2.2](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.2.2).

## The teaching approach

Start with a visible result. Use **show → predict → try → explain**. Students copy complete commands and change one meaningful value. Do not require them to write a Python program from scratch or understand the container internals.

Success means each student moves the virtual bus, observes a ROS message, sends one LED command to the real robot and explains who sends and who receives. If time allows, add a short physical movement. Students may work in pairs but must swap roles.

Turtlesim is standard ROS Turtlesim with a new picture, not a physical model of RBussi. It does not simulate our line sensors, slip or motor calibration. The two systems use different command types; say this explicitly instead of implying that the exact same commands already control both.

## Preparation

- Download both container archives and the extracted kit beforehand. Prefer loading ready-built images to building during class.
- Prepare one working instructor computer and a spare working station. Docker setup can require a reboot or virtualization configuration; do not promise that every installation will finish within one short slot.
- Open the browser simulator before class. Test keyboard focus and movement. Keep the real robot's motor power off during the simulator part.
- Prepare charged batteries, white/black sensor patches, board files and individual account cards. Credentials stay private and are never projected.
- Rehearse `robot-connect` on the instructor robot. It is intentionally separate from starting the simulator.
- If Moodle completion remains required, reserve the alternative final block below rather than silently replacing remote-lab work.

## Sequence

| Time | Students do | Instructor explains | Check |
|---|---|---|---|
| 13:00–13:10 | Watch the virtual bus and a real-robot LED demo | Today: send commands and receive information | Identify virtual versus real robot |
| 13:10–13:45 | Load the container and open its browser desktop | A prepared workspace; no ROS installation on the host | Everyone sees bus + terminal, individually or in pairs |
| 13:45–14:05 | Move the virtual bus using arrow keys | Keyboard program sends movement messages | Each student drives and turns |
| 14:05–14:25 | List topics and view `/turtle1/pose` | Topic = named channel; message = content | Identify x, y and direction |
| 14:25–14:40 | Break | — | — |
| 14:40–15:00 | Send a velocity message from the terminal | `linear.x` is forward/backward; `angular.z` is turning | Straight motion, turn, then optional arc |
| 15:00–15:15 | Trace keyboard → topic → simulator | Node, publisher, subscriber | Explain the path in ordinary words |
| 15:15–15:40 | Upload ready-made board files and connect the MQTT bridge | Same message idea, now connected to real hardware | ESP32 READY and bridge MQTT connected |
| 15:40–15:50 | Break | — | — |
| 15:50–16:10 | Switch real LED ON/OFF and read line sensors | Commands go out; sensor data comes back | One real output and one real input |
| 16:10–16:25 | Request short physical movement, wheels lifted | Timed commands, motor power, local stopping | Forward and stopping |
| 16:25–16:45 | Paired mini-challenge or one small Python edit | Predict, change, observe | Both partners participate |
| 16:45–17:00 | Explain, save and shut down | Review the two paths | Individual explanation; motor power off |

## 13:00–13:10 — Show the result

Move the simulated bus. Then switch a real robot's LED on and off.

Say:

> “We will first practise with a virtual robot. Then we will connect to the robot on your desk. The setup code is ready; today you will use messages and understand what they do.”

Ask which actions affected a picture and which affected hardware. Explain that the RBussi graphic uses their robot's shape and colours, but does not reproduce all its physical behaviour.

## 13:10–13:45 — Start the prepared workspace

Use README steps 1, 2 and 6 for simulation. No board or account configuration is needed yet. Load the correct AMD64/ARM64 archive, run `docker compose up -d`, then open:

**http://localhost:6080/vnc.html?autoconnect=true&resize=scale**

Say:

> “Docker opens a prepared workspace containing ROS, the simulator and a terminal. We will use the tools inside it.”

Always label commands by location:

- **COMPUTER TERMINAL:** Docker commands outside the container.
- **BROWSER ROS TERMINAL:** commands inside the prepared workspace.
- **THONNY / ROBOT:** uploading board files later.

This distinction matters more than teaching Linux terminology. If one computer remains blocked after about 15 minutes of individual troubleshooting, pair its student with a working station. Continue the lesson and return to installation later. The 35-minute setup slot is a budget, not a promise that every Docker installation can be repaired in that time.

## 13:45–14:05 — Move with the keyboard

In the browser terminal:

```sh
ros2 run turtlesim turtle_teleop_key
```

Click inside that terminal and use the arrows. The simulator window itself does not receive keyboard commands. Demonstrate this common focus issue explicitly.

Tasks: move forward, turn, move again, then move backward. Partners swap. Stop sending keys to observe the short motion timeout; Ctrl+C ends the keyboard program.

Say:

> “The keyboard program sends instructions. A separate program draws the bus and moves it.”

Do not explain every word in the launch command yet.

## 14:05–14:25 — Look at the messages

After Ctrl+C, run:

```sh
ros2 topic list
ros2 topic echo /turtle1/pose
```

Explain `x`, `y` and `theta` as horizontal position, vertical position and heading. Radians can remain a supplied unit today; students only need to notice that turning changes heading.

Use `ros-terminal` to open another terminal if students want to drive while watching the data. Otherwise demonstrate this on the instructor computer. Ctrl+C stops the viewer, not the simulator.

Say:

> “A topic is a named channel. The simulator sends its position on this channel, and our viewer receives it.”

The names `turtle1` and `turtlesim` are kept deliberately so standard ROS tutorials still work.

## 14:40–15:00 — Send a command directly

Copy into the browser ROS terminal:

```sh
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.0}}"
```

Explain only four meaningful parts: the channel `/turtle1/cmd_vel`, `--once` (one message), `linear.x` (forward/backward velocity) and `angular.z` (turning velocity). Treat `geometry_msgs/msg/Twist` as the supplied velocity-message type.

Ask students to predict negative `linear.x`. Then use zero linear motion and nonzero angular motion to turn. Combining both makes an arc. Do not explain every Twist field or YAML punctuation.

Clarify that this is a velocity request, not a destination. The simulator stops after its command timeout. A supplied reset command is available in SIMULATOR.md; services are not a required new concept today.

## 15:00–15:15 — Name the parts

Show `ros2 node list` and draw:

```text
keyboard program → /turtle1/cmd_vel → simulator
simulator → /turtle1/pose → message viewer
```

| Term | Simple explanation |
|---|---|
| Node | A running ROS program |
| Topic | A named channel |
| Publisher | A sender on a topic |
| Subscriber | A receiver on a topic |

A program can send on one channel and receive on another. Let students explain the picture before introducing the physical-robot bridge.

## 15:15–15:40 — Connect the real robot

Now draw:

```text
ROS program ↔ bridge ↔ MQTT broker ↔ ESP32 MicroPython
```

Follow README robot/configuration steps. Keep motor power off. Back up an existing main.py before uploading. Use the account's exact prefix and different PC/ESP32 client IDs. Disconnect MQTTX/Explorer if it uses the PC ID.

Reset the ESP32 and find `READY`. After adding `settings.env`, run `docker compose up -d --force-recreate` on the computer. This restarts the desktop and clears the simulator drawing. Reopen the browser if necessary.

In one ROS terminal:

```sh
robot-connect
```

Find `MQTT connected`. Leave this terminal running. Open another terminal with `ros-terminal` for commands.

Say:

> “ROS stays on the computer. MicroPython stays on the robot. The bridge translates our messages between ROS and MQTT.”

Launching the simulator alone never starts this bridge. The arrows controlling Turtlesim do not move the physical robot.

## 15:50–16:10 — LED first, then sensors

Use the student's robot number:

```sh
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'ON'}"
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'OFF'}"
ros2 topic echo /robot01/line
```

Explain String as a text message. Students identify the topic and the content, just as in simulation. Here the content is ON/OFF rather than a velocity structure.

Move white paper and black patches below the sensors. Read only the values under `data`: `[left, right]`, white 0, black 1. Ignore layout metadata today. Partners swap keyboard and paper roles.

Ask: “Who sends the sensor reading? Who receives it?” Distinguish the ESP32's MQTT publication from the bridge's ROS publication.

## 16:10–16:25 — Physical movement

Lift wheels, enable motor power and keep the switch accessible. Send once:

```sh
ros2 topic pub --once /robot01/move std_msgs/msg/String "{data: 'forward'}"
```

Wait for stopping before another request. Try backward or a turn if time allows. Demonstrate `stop` from a prepared second terminal so beginners need not type quickly.

Explain: the prepared program limits the duration; timed movement is not a measured distance or angle. PWM is not measured speed. Network commands can be delayed, so the physical power switch remains the immediate stop.

Explicit comparison:

- Simulation: Twist velocities on `/turtle1/cmd_vel`; ideal position is known.
- Real robot: String commands on `/robot01/move`; no wheel encoders or measured pose.
- There is no automatic `cmd_vel` → motor conversion in this kit.

## 16:25–16:45 — Small challenge, no compulsory coding

Each pair demonstrates one simulated movement, one real sensor change and one real LED command. Each student explains one message path.

Optional programming: run `python examples/01_led.py`, stop it, change the timer from 1.0 to 0.5 seconds on the computer, save and rerun. Explain that this script runs in ROS on the computer; it is not uploaded to the ESP32. Do not require a line-by-line explanation of classes or `self`. Send LED OFF afterwards.

Faster students can request a beep or attempt the sensor-to-LED extension. Do not add compulsory JSON wheel control, services or new wiring.

## 16:45–17:00 — Checkpoint and shutdown

Ask each student one question: where does ROS run; what is a topic; which program receives the command; does closing a viewer stop the physical robot?

Accept ordinary-language explanations. Assess understanding and personal participation, not typing speed or memorization. Save edited examples. Send `stop`, switch motor power off, send LED OFF, close the bridge and run `docker compose down` in the computer terminal. The ESP32 remains independently powered until switched off; main.py starts on its next reset and waits for commands.

## If Moodle completion is still required

At 16:10, skip physical movement, Python editing and the extended challenge. Use 16:10–16:15 for a short ROS checkpoint, 16:15–16:50 for the remote laboratory/Moodle, then 16:50–17:00 to save and shut down. Allocate remote-robot access and use supported simulation while waiting. This block does not guarantee completion of every outstanding Moodle task; check remaining work explicitly.

## Leave for another lesson

Services/actions in depth, package builds, DDS/QoS internals, custom messages, `cmd_vel` conversion for the physical robot, odometry, RViz, Gazebo and SLAM. The simulator picture is an entry point to ROS concepts, not evidence of a calibrated robot model.
