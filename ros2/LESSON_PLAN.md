# Instructor plan: first steps in ROS 2 with a real robot

**Audience:** robotics beginners, including students with no programming experience.  
**Session:** 13:00–17:00. This is a proposed ROS introduction, not a requirement to finish every optional ROS exercise.  
**Language:** English student explanations and materials.  
**Materials:** [setup](README.md), [exercises](EXERCISES.md), [ready-made kit and images](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.1.0).

## What counts as success

Every student should be able to send one LED command, observe one real sensor change, request a short movement and explain which program sends and which program receives a message. Working in a pair is acceptable; both students must take a turn at the keyboard and explain one result.

Writing a program from scratch, understanding Python classes, installing ROS natively, building Docker images, and learning services/actions are not objectives today. Reading and changing one line of supplied Python is an optional next step.

Use the same teaching pattern throughout: **show → predict → try → explain**. Give one small task at a time. After a short demonstration, leave its exact command and expected result visible. Introduce terminology when students have something concrete to attach it to.

## Prepare before students arrive

- Charge the robot batteries. Prepare white paper and black patches. Test the instructor robot, Wi-Fi, MQTT and container.
- Download both image archives to a USB drive: AMD64 about 339 MB, ARM64 about 322 MB. Have the extracted kit ready. Students should load images, not build them.
- Have one known-working computer as a fallback. Docker installation may require a restart or virtualization setup; the setup slot below is a time budget, not a guarantee that every laptop can be fixed in 45 minutes.
- Prepare each student's robot number, exact topic prefix and distinct PC/ESP32 client IDs. Supply credentials privately. Never project a filled-in configuration.
- Prepare copyable commands with `robot01` clearly marked as the part to replace. Avoid manual typing of long commands.
- Have the board files ready in one folder. Back up existing `main.py` files. Keep motor power off while uploading.
- Decide whether Moodle completion is still required in this session. If so, use the alternative ending below; do not silently replace required remote-lab work with optional ROS tasks.

## Schedule

| Time | What students do | What the instructor explains | Completion check |
|---|---|---|---|
| 13:00–13:10 | Watch LED, sensors and a short movement | Today's goal: control a real robot from another program | Predict what one command will do |
| 13:10–13:20 | Trace one message on a simple diagram | Robot, computer, broker; ROS runs on the computer | Identify where ROS runs |
| 13:20–14:05 | Upload robot files, load image, start the bridge | Only the steps needed to launch the prepared environment | Board READY and bridge MQTT connected |
| 14:05–14:25 | Turn the built-in LED ON and OFF | A topic is a named channel; a message is its content | Each student controls the LED |
| 14:25–14:40 | Break | — | — |
| 14:40–15:05 | Read the two line sensors | Receiving messages; left/right array; repeated readings | Change one value by moving paper |
| 15:05–15:30 | Send forward, backward, turn and stop | Same message pattern, another output; local time limit | One short motion and stopping |
| 15:30–15:40 | Break | — | — |
| 15:40–15:55 | Inspect nodes/topics and explain the path | Node, publisher, subscriber and bridge | Explain one command and one sensor message |
| 15:55–16:15 | Run a ready-made Python node; change one value | A script can send the same message as the terminal | Observe the effect of one edit |
| 16:15–16:35 | Complete a small paired demonstration | Combine familiar steps; no new required concepts | Partner can reproduce the demonstration |
| 16:35–17:00 | Demonstrate, explain, save and shut down | Review; stop versus closing a viewer; next steps | Individual explanation and robot safely stopped |

## 13:00–13:10 — Start with the result

Use the instructor's already-connected robot. Switch its LED on and off, move paper below a sensor, then demonstrate a short movement with wheels lifted.

Say:

> “Today we will send instructions to a real robot and receive information from it. The difficult setup code is already provided. You will use it first, then change a small part yourself.”

Ask: “What information did the computer send? What information did the robot send back?” Accept ordinary words such as “turn on” and “black”. Do not begin with installation instructions or a list of ROS terminology.

## 13:10–13:20 — One picture, three locations

Draw or show:

```text
Computer: ROS programs + bridge ↔ MQTT broker ↔ Robot: MicroPython
```

Say:

> “The robot still uses the MicroPython program we know. The broker carries its messages. ROS lets programs on the computer exchange messages and work together. Our bridge translates between the two sides.”

Explain Docker in one sentence:

> “The container is our prepared workspace, with ROS and the necessary tools already installed.”

Explain why ROS is useful: separate programs can handle sensing, decisions and commands; standard tools let us inspect their communication. MQTT remains useful for the existing robot connection. Our container does not put ROS on the ESP32.

Do not teach DDS, network discovery, image layers or Linux administration here.

## 13:20–14:05 — Guided setup, with visible checkpoints

Follow [README.md](README.md), one checkpoint at a time. Label the instruction currently on screen:

- **THONNY / ROBOT:** upload files and edit board settings.
- **COMPUTER TERMINAL:** Docker commands, outside the container.
- **ROS TERMINAL:** opened by `docker compose exec ros bash`.

The distinction between these three places matters more than terminal terminology.

Suggested pacing:

1. **13:20–13:30:** extract kit, identify AMD64/ARM64, start Docker installation/check. Begin image loading as soon as Docker is ready.
2. **13:30–13:45:** upload supplied robot files in Thonny; keep MicroPython already installed. Set credentials privately. Reset the board and find `READY: ...`.
3. **13:45–14:00:** complete private `settings.env`, load the image, run `docker compose up -d`, find `MQTT connected` in logs. Disconnect MQTTX/Explorer if it uses the same PC client ID.
4. **14:00–14:05:** enter the ROS terminal. Pair students whose computers are still blocked with a working station.

A student can say “ready” only after checking the message, not simply because a command produced no error. Remind them that `TOPIC_PREFIX` has no leading slash and no `/status` suffix.

If one laptop remains blocked after about 15 minutes of individual troubleshooting, continue in a pair and return to installation later. Do not let the whole class wait for one Docker installation. Students without a running container can still complete the message exercises on their partner's computer; they should use that station's assigned robot namespace.

## 14:05–14:25 — First success: the LED

Use the built-in LED, so no new wiring is needed. Motor power remains off. Commands run in the **ROS TERMINAL**:

```sh
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'ON'}"
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'OFF'}"
```

First demonstrate ON. Ask students to predict the change needed for OFF. Then let everyone do both.

Explain only:

- `/robot01/led`: the named channel for this robot's LED.
- `ON`: the content of the message.
- `--once`: send one message.
- `std_msgs/msg/String`: the message contains text. Students may copy this fixed part today.

Say:

> “The channel tells us where the message goes. The text tells the receiving program what to do.”

Do not explain every token, YAML syntax or ROS package naming. Check the actual LED before moving on. If it does not respond, check the robot number, board READY and bridge connection; do not change several settings at once.

## 14:40–15:05 — Listen to the robot

In the **ROS TERMINAL**:

```sh
ros2 topic echo /robot01/line
```

Say:

> “Before, we sent a message. Now we listen. The robot sends two numbers: left sensor, then right sensor.”

Ignore the `layout` and `data_offset` fields for this lesson. Point to the two values under `data`.

Tasks:

1. Put white under both sensors. Predict and observe `[0, 0]`.
2. Put black under the left sensor only. Observe `[1, 0]`.
3. Switch sides and observe `[0, 1]`.
4. Put black under both and observe `[1, 1]`.

Physically confirm which sensor is left if the mapping differs. Let partners swap keyboard/paper roles.

Ask: “Why do messages continue when the paper is not moving?” The prepared program sends readings periodically.

Ctrl+C stops this **viewer**. It does not shut down the bridge or stop the robot application. Avoid using “Ctrl+C stops the robot” as a general statement.

## 15:05–15:30 — Use the same pattern for movement

Lift wheels first, then enable motor power. Keep the power switch accessible. Copy:

```sh
ros2 topic pub --once /robot01/move std_msgs/msg/String "{data: 'forward'}"
```

Say:

> “Only the topic and the message changed. The robot already knows how to interpret forward. It moves briefly and stops by itself.”

Students try one command at a time, waiting for stopping. Replace `forward` with `backward`, then `left` and `right`. Demonstrate `stop` from a prepared second terminal while the robot moves; beginners do not need to type it quickly:

```sh
ros2 topic pub --once /robot01/move std_msgs/msg/String "{data: 'stop'}"
```

Explain three practical points:

- Forward/backward last one second; turns last 400 ms. They do not specify centimetres or degrees.
- PWM is motor power control, not measured speed. The robot has no wheel encoders.
- A message can be delayed. The local timeout helps, but the motor-power switch is the immediate physical stop.

Do not introduce JSON wheel commands or `cmd_vel` in the required part. If a robot does not move, check motor battery and power before changing ROS code.

## 15:40–15:55 — Give names to what students have seen

Now introduce the four core terms:

| Term | Plain explanation | Example today |
|---|---|---|
| Node | A running ROS program | Our MQTT bridge |
| Topic | A named message channel | `/robot01/line` |
| Publisher | A sender on a topic | The bridge sends sensor readings into ROS |
| Subscriber | A receiver on a topic | `topic echo` receives those readings |

A node can both publish and subscribe. The bridge subscribes to ROS commands and publishes ROS sensor readings. MQTT topic names, such as `edu-2026-10/robot01/cmd/led`, are separate from ROS topic names.

Show:

```sh
ros2 node list
ros2 topic list
```

Ask two students to explain the path in opposite directions:

- LED: terminal publisher → ROS topic → bridge → MQTT → ESP32 → LED.
- Sensor: ESP32 → MQTT → bridge → ROS topic → terminal subscriber.

Clarify that today we use a prepared bridge; students do not need to understand its entire implementation.

## 15:55–16:15 — One small Python edit

This block is optional if setup or basic exercises needed more time. Start with the LED, not a new movement program:

```sh
python examples/01_led.py
```

Ask students to observe the repeating LED changes. Then show just:

```python
self.create_timer(1.0, self.blink)
```

Say:

> “This number says how often to run the blink function. Predict what happens if we change 1.0 to 0.5.”

Stop the example with Ctrl+C, edit the file on the **computer**, save it, then run the command again in the **ROS TERMINAL**. Make clear that this Python file runs on the computer in the container; it is not uploaded to the ESP32.

Explain `self` and classes only if asked; they are prepared structure today. Avoid walking through imports and boilerplate line by line. One understood change is enough. Send LED OFF afterwards.

Faster students may run `02_read_line.py`, identify its callback and change one printed message. Students comfortable with programming may attempt the sensor-to-LED extension from EXERCISES.md. Do not require novices to combine two programs independently.

## 16:15–16:35 — Paired mini-challenge

One student operates; the other predicts and explains. Then swap.

Required demonstration:

1. Show a real sensor value changing.
2. Switch the LED ON and OFF through ROS.
3. Request one short movement with wheels lifted; observe the stop.
4. Point to the topic and message in one command.

A learner still working on setup may use the partner's computer. Stronger students can add one optional feature: sound, a modified blink interval, or a sensor-to-LED node. The goal is a repeatable result, not a race to complete every extension.

## 16:35–17:00 — Explain, save and finish

Ask each student one small question and accept an explanation in ordinary language:

- “Where does ROS run?”
- “What is the difference between the topic and the message?”
- “Which program sends the sensor readings into ROS?”
- “Does closing the sensor viewer stop the robot?”

Do not grade typing speed or memorization of command syntax. Check that everyone has personally performed an action, not only watched a partner.

Send `stop`, switch motor power off, send LED OFF, save edited examples, and exit the ROS shell. Run `docker compose down` in the **COMPUTER TERMINAL**. Keep private account files private. Explain that the ESP32's `main.py` starts again when the board is powered/reset; it waits for commands rather than moving immediately.

## If remote-lab / Moodle completion is still required

Keep the same plan through 15:55, then use:

| Time | Activity |
|---|---|
| 15:55–16:05 | ROS mini-checkpoint: LED, sensor message, explain the path |
| 16:05–16:50 | Remote laboratory and unfinished Moodle assignments |
| 16:50–17:00 | Save work, check completion and shut down |

Skip Python editing and extra ROS challenges. They are optional. Allocate remote-robot access in advance and use supported simulation while waiting; assess Moodle progress in the remote course itself, not by successful local ROS commands. This 45-minute block does not guarantee completion of all outstanding assignments.

## What to leave for a later lesson

Services, actions, launch files, custom ROS messages, building packages, DDS/QoS internals, `cmd_vel` conversion, odometry, RViz, Gazebo and SLAM. The prepared kit contains no simulator. None is needed to achieve today's first ROS result with a real robot.
