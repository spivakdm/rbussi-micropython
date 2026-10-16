# ROS 2 with RBussi

Kit 0.2.7, container 0.2.7. English classroom slides.

## 1. ROS 2 with RBussi

Introduction to Mobile Robotics
with a Remote Laboratory

Metropolia ICT Summer School
Dmitrii Spivak

Simulation first. Then your robot.





Instructor note: Course TX00GZ66-3001, 3 ECTS. Session 13:00–17:00. Prepared kit version 0.2.7.

## 2. Today’s exercises

1. Start the prepared ROS workspace.
2. Drive the virtual bus and explore ROS topics.
3. Write a subscriber and a publisher.
4. Follow the line with your own ROS node.
5. Connect and control your physical robot.

Work in pairs if setup takes longer. Swap roles.



Instructor note: Suggested timing: setup until 13:35, keyboard and topics until 14:10, break to 14:20, student templates to 15:25, break to 15:35, physical setup to 16:00, hardware to 16:35, checkpoint and shutdown until 17:00.

## 3. Where commands run

COMPUTER TERMINAL
PowerShell or Terminal: docker commands.

BROWSER ROS TERMINAL
Inside the VNC desktop: ros2 and Python examples.

THONNY / ROBOT
Upload MicroPython files to the ESP32.

Each command slide names the terminal you need.



Instructor note: 

## 4. Docker installation

COMPUTER TERMINAL

Windows / macOS: install and start Docker Desktop.
Windows: use Linux containers with WSL 2.
Linux: install Docker Engine + Compose plugin.

```bash
docker version
docker compose version
```

Check for Client AND Server. Compose 2.24 or newer.

[Docker Desktop](https://docs.docker.com/desktop/)
[Docker Engine](https://docs.docker.com/engine/install/)

Instructor note: Windows setup may need virtualization, WSL and a restart. Pair students on a working station after about 15 minutes of individual troubleshooting. Source: ros2/README.md.

## 5. Two downloads

Download and extract RBussi-ROS-kit-v0.2.7.zip.

Choose ONE container image:
Intel / AMD computers: amd64.tar.gz
Apple Silicon Macs / ARM64 Linux: arm64.tar.gz

Place the image beside compose.yaml.

Keep the .tar.gz compressed. About 500 MB.

[Download kit 0.2.7 and image links](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.2.7)

Instructor note: Full image names on the next slide. Intel Macs use amd64. Windows ARM has not been rehearsed. Students may download in advance or use an instructor-provided copy.

## 6. Load the container image

COMPUTER TERMINAL

Open a computer terminal in the extracted kit folder.
Use the command for your processor.

```bash
docker load -i rbussi-ros-0.2.7-amd64.tar.gz

# Apple Silicon / ARM64 instead:
docker load -i rbussi-ros-0.2.7-arm64.tar.gz
```

One-time step. Run only the matching command.



Instructor note: 

## 7. Start the workspace

COMPUTER TERMINAL

Run this in the folder containing compose.yaml.

```bash
docker compose up -d
```

Browser: http://localhost:6080/vnc.html

[Open browser desktop](http://localhost:6080/vnc.html?autoconnect=true&resize=scale)

Instructor note: No settings.env or MQTT account is needed for simulation. Starting the desktop does not connect to the real robot.

## 8. The browser desktop

Left: the simulated RBussi.
Right: your ROS terminal.

Click inside the terminal before typing.
Ctrl+C ends the current command.
F8 opens another terminal.

The picture resembles RBussi. Its physics are standard Turtlesim.



Instructor note: Show the live desktop. Keep real motor power off during simulation. sim-line-track adds ideal digital line sensors. The simulation does not model wheel slip, calibration or measured real-robot pose. If input is uppercase, check Caps Lock. Version 0.2.7 fixes click-to-focus.

## 9. Exercise 1: keyboard control

BROWSER ROS TERMINAL

Click inside the browser terminal. Run:

```bash
ros2 run turtlesim turtle_teleop_key
```

Up/Down: move. Left/Right: turn. Ctrl+C: exit.



Instructor note: Keep keyboard focus in the terminal. Up/Down move forward/backward; Left/Right turn. Stop sending keys and motion stops after a short timeout. Ctrl+C returns to the shell. The front points right at startup.

## 10. A node is a running ROS program

A node does one job and exchanges messages.

/teleop_turtle: reads your keyboard.
/turtlesim: moves and draws the virtual robot.
/robot01/mqtt_bridge: connects ROS to MQTT.

One node can send messages and receive messages.



Instructor note: Run keyboard control in a second terminal before showing /teleop_turtle. The executable turtle_teleop_key creates the node /teleop_turtle. Closing a program removes its node. Source: ROS 2 Jazzy Understanding Nodes.

## 11. A topic is a named channel

The keyboard sends velocity messages to the simulator.

Publisher = sender. Subscriber = receiver.



Instructor note: The middle box is a named channel, not another running program or a broker. ROS nodes exchange typed messages over topics. Multiple publishers and subscribers are possible. This diagram shows the classroom example.

## 12. The simulator also publishes

The simulator sends its position. A viewer receives it.

A topic viewer receives data without controlling the robot.



Instructor note: ros2 topic echo creates a temporary ROS node with a subscription. /turtle1/pose uses turtlesim/msg/Pose. x and y are position, theta is heading. Ctrl+C stops the viewer, not Turtlesim.

## 13. Topic, message type and message

Topic: the channel name, /turtle1/cmd_vel.
Type: the structure, geometry_msgs/msg/Twist.
Message: one set of values in that structure.

```bash
{linear: {x: 1.0}, angular: {z: 0.0}}
```

Here: forward velocity 1.0, turning velocity 0.0.



Instructor note: A message type defines fields. Twist has linear and angular vectors, each with x, y, z. Unspecified fields default to zero in this CLI request. linear.x means forward relative to the robot, not screen horizontal. angular.z is yaw rate in radians/second.

## 14. Exercise 2: discover ROS

BROWSER ROS TERMINAL

Press Ctrl+C to leave keyboard control.

```bash
ros2 node list
ros2 topic list
```

Find /turtle1/cmd_vel and /turtle1/pose.



Instructor note: Node: a running ROS program. Topic: a named channel for messages. A publisher sends, a subscriber receives. turtle_teleop_key disappears from the node list when stopped. Keep the standard turtle names even though the sprite is RBussi.

## 15. Exercise 3: watch position

BROWSER ROS TERMINAL

In one terminal, watch the position:

```bash
ros2 topic echo /turtle1/pose
```

x, y: position. theta: heading in radians.



Instructor note: Open another terminal with F8 and run keyboard control there. Ask which value changes when turning. Ctrl+C ends the viewer. The simulator continues running. No need to teach radian conversions today.

## 16. Exercise 4: one movement

BROWSER ROS TERMINAL

Stop keyboard control with Ctrl+C. Send one message:

```bash
ros2 topic pub --once /turtle1/cmd_vel \
  geometry_msgs/msg/Twist \
  "{linear: {x: 1.0}, angular: {z: 0.0}}"
```

Try x: -1.0. Predict the direction first.



Instructor note: Backslashes continue one command across lines in the browser Bash terminal. Twist is the velocity-message type. linear.x requests velocity, not a destination or one-metre trip. Turtlesim stops roughly one second after the last command.

## 17. Exercise 5: turns and arcs

BROWSER ROS TERMINAL

Change the values in the previous command.

Turn in place:     x: 0.0     z: 1.0
Turn the other way:     x: 0.0     z: -1.0
Draw an arc:     x: 1.0     z: 1.0

```bash
ros2 service call /reset std_srvs/srv/Empty "{}"
```

Reset clears the trail and restores the starting pose.



Instructor note: The x values refer to linear.x and z to angular.z inside Twist. Treat reset as a supplied helper, not a new topic for detailed teaching. The drawn trail is not a simulated line-following track.

## 18. The publish command, explained

ros2 topic pub     Publish a message.
--once                 Send one message.
/turtle1/cmd_vel    Choose the channel.
geometry_msgs/msg/Twist    Choose the type.
{linear: ..., angular: ...}    Supply the values.

--once counts messages. It does not specify motion duration.



Instructor note: The backslash at a line end continues a Bash command. Turtlesim stops roughly one second after the last velocity message. Other robot controllers may behave differently. Keep the distinction between velocity and destination explicit.

## 19. Explore the running system

BROWSER ROS TERMINAL

These commands describe what is available now.

```bash
ros2 node list
ros2 node info /turtlesim
ros2 topic list -t
ros2 topic info /turtle1/cmd_vel
```

Try it: find the simulator’s input and output topics.



Instructor note: node list lists discovered nodes; node info shows their interfaces. topic list -t includes message types. topic info shows type and publisher/subscriber counts. A topic may exist even if no messages currently arrive.

## 20. Where to find commands

BROWSER ROS TERMINAL

ROS help explains the tools and message fields.

```bash
ros2 --help
ros2 topic pub --help
ros2 interface show geometry_msgs/msg/Twist
```

RBussi movement words: forward, backward, left, right, stop.

[RBussi command examples](https://github.com/spivakdm/rbussi-micropython/blob/main/ros2/EXERCISES.md)

Instructor note: ROS sees a String on /robot01/move. The ESP32 application defines accepted words; ROS introspection cannot enumerate these application-level values. Consult the RBussi exercises for commands and limits.

## 21. Your own line-following node



Simulation first. No MQTT account or physical robot needed.

Instructor note: Learning goal: read two sensors, choose a movement, publish a velocity. Track is generated by sim-line-track. The city map is property of Robotx Oy; reuse requires permission.

## 22. Student files

Download RBussi-ROS-student-templates.zip.
Extract it into your kit folder, beside compose.yaml.
Edit the Python files on your computer.
Run them in the browser ROS terminal.

```bash
examples/student/01_sensor_subscriber.py
examples/student/02_velocity_publisher.py
examples/student/03_line_follower.py
```

Keep the TODOs for yourself: complete one file at a time.

Instructor note: The examples folder is shared with /course/examples inside the container. Open files in a local text editor, including Thonny as an editor. Do not run these ROS programs on the ESP32 or with local MicroPython. No image rebuild is needed.

## 23. The track and its sensors

Stop teleop or sim-line-demo with Ctrl+C first.
Terminal A: start the track and leave it running.
Terminal B: inspect the sensor messages.

```bash
sim-line-track

# In terminal B (F8):
ros2 topic echo /sim/line
```

data: [left, right]     White = 0     Black = 1

Instructor note: sim-line-track supplies sensors and resets the starting pose but does not drive. sim-line-demo already runs a controller; do not run it together with the student controller. Ctrl+C stops the topic viewer. The markers are cyan on white and red on black.

## 24. Your subscriber

Task 1: receive and print the two sensor values.
Complete create_subscription(...) in file 01.
Type: Int32MultiArray     Topic: /sim/line
Callback: show_sensors

```bash
cd /course/examples/student
python 01_sensor_subscriber.py
```

Can you explain when show_sensors(message) is called?

Instructor note: Allow 15 minutes. Look at ros2 topic info /sim/line and ros2 interface show std_msgs/msg/Int32MultiArray. The starter contains the callback. Stop with Ctrl+C before the next task. Teacher answers: ros2/teacher/STUDENT_SOLUTIONS.md.

## 25. Your publisher

Task 2: send velocity commands in file 02.
Create a Twist publisher on /turtle1/cmd_vel.
Choose linear.x = 0.5 and publish the message.
The supplied timer sends zero speed after 3 seconds.

```bash
python 02_velocity_publisher.py
```

linear.x: forward speed     angular.z: turning speed

Instructor note: Allow 15 minutes. Complete all three TODOs. Publishing repeats every 0.05 seconds. The program stays running after three seconds, publishing zero; Ctrl+C exits. Stop it before the follower, otherwise two publishers compete. Simulator values are not PWM percentages.

## 26. Your relay controller

Task 3: complete choose_motion(left, right) in file 03.

| Left | Right | Action | Forward, turn |
|---|---|---|---|
| 0 | 0 | Straight | 0.9, 0.0 |
| 1 | 0 | Left | 0.5, 1.8 |
| 0 | 1 | Right | 0.5, -1.8 |
| 1 | 1 | Stop | 0.0, 0.0 |

Use if / elif / else. Return two numbers: forward, turn.

Instructor note: Allow 25 minutes including the next slide. Both white assumes the narrow black line is between sensors. It can also mean a lost line: two binary sensors cannot distinguish these situations. Both black means stop. Starter code handles subscriptions, publishing and missing sensor data.

## 27. One complete lap

Stop your previous movement program with Ctrl+C.
Restart sim-line-track to reset the starting position.
Leave it running, then run your follower in terminal B.

```bash
cd /course/examples/student
python 03_line_follower.py
```

Watch one full lap. Change one speed value and try again.

Instructor note: Only one velocity controller at a time. Do not run sim-line-demo simultaneously. The supplied controller wrapper publishes zero if sensor data is absent for more than 0.5 seconds. Stop the track to demonstrate this. Turtlesim also has its own command timeout. Physical robot remains disconnected.

## 28. Your node in the ROS graph

Task 4: identify your node, its input and its output.
Input: /sim/line     Output: /turtle1/cmd_vel
Stop the sensor program: does your bus stop?

```bash
ros2 node info /student_line_follower
rqt_graph
```

Explain the message path to your partner before using hardware.

Instructor note: Allow 10 minutes. Graph: sim_line_sensors publishes /sim/line; student_line_follower subscribes and publishes /turtle1/cmd_vel; turtlesim subscribes and publishes /turtle1/pose back to the sensor node. Refresh rqt_graph if needed. No MQTT is involved. Next block connects the physical robot through a separate bridge.

## 29. ROS and MQTT reach the real robot

ROS runs on the computer. MicroPython runs on the ESP32.

Turtlesim is separate. Its arrow keys do not move the real robot.



Instructor note: Command path: ROS String on /robot01/move reaches /robot01/mqtt_bridge, which publishes to edu-2026-10/robot01/cmd/move through mqtt.ondroid.org. Telemetry returns from the ESP32 through the broker and bridge to ROS /robot01/line. ROBOT_NAME and MQTT_PREFIX select robot01. The ESP32 is not a ROS node in this kit.

## 30. Real robot: board files

THONNY / ROBOT

Keep motor power off. Back up your old main.py.
Copy network_secrets.example.py to network_secrets.py.
Enter your Wi-Fi and assigned MQTT account.

Upload from the kit’s robot folder:
main.py, robot.py, drive_command.py, robot_mqtt.py,
network_secrets.py and the complete umqtt folder.

Reset the board. Look for READY in Thonny.

[Full robot setup](https://github.com/spivakdm/rbussi-micropython/blob/main/ros2/README.md)

Instructor note: Use ordinary 2.4 GHz Wi-Fi. Upload to the board root with Thonny View > Files. MicroPython remains installed; no reflashing if already prepared. If the ROS board files are already installed and working, skip upload. Do not show private credentials on the projector. Exact MQTT prefix example: edu-2026-10/robot01, without /status.

## 31. Real robot: computer settings

COMPUTER TERMINAL

Copy settings.env.example to settings.env.
Enter your MQTT account and assigned robot number.
Use different PC and ESP32 client IDs.

Save the file, then run:

```bash
docker compose up -d --force-recreate
```

Reopen the browser. This restarts the simulator.



Instructor note: Host mqtt.ondroid.org, TCP port 1883. Use private credentials from the account card. MQTT_PREFIX=edu-2026-10/robot01 and ROBOT_NAME=robot01. PC client ID edu-2026-10-robot01-pc; board client ID ends -esp32. Close MQTT Explorer/MQTTX if using the same PC client ID. No TLS certificate for TCP/1883; credentials travel unencrypted.

## 32. Real robot: start the bridge

BROWSER ROS TERMINAL

Run this in a browser terminal:

```bash
robot-connect
```

Wait for MQTT connected. Leave this running.
F8: open a second terminal for commands.



Instructor note: Use F8 to open a second terminal for all following commands. Bridge translates between ROS topics and MQTT topics. ESP32 still runs MicroPython. If no telemetry arrives, check board READY, Wi-Fi, exact prefix and unique client IDs. Simulator arrows do not control the physical robot.

## 33. Exercise 6: LED ON / OFF

SECOND BROWSER ROS TERMINAL

Use your robot number instead of robot01.

```bash
ros2 topic pub --once /robot01/led \
  std_msgs/msg/String "{data: 'ON'}"

ros2 topic pub --once /robot01/led \
  std_msgs/msg/String "{data: 'OFF'}"
```

Check the real LED. String means a text message.



Instructor note: Keep the bridge terminal running. Built-in user LED is GPIO2. One student sends, the other observes, then swap.

## 34. Exercise 7: real sensors

SECOND BROWSER ROS TERMINAL

Hold white paper, then black under each sensor.

```bash
ros2 topic echo /robot01/line
```

data: [left, right]     White = 0     Black = 1



Instructor note: Ignore layout metadata in Int32MultiArray today. Left A3/GPIO34, right A2/GPIO35. Ctrl+C stops only the viewer. Ask who publishes the sensor data: ESP32 via MQTT, then bridge via ROS.

## 35. Exercise 8: move and stop

SECOND BROWSER ROS TERMINAL

Lift the wheels. Enable motor power. Send once:

```bash
ros2 topic pub --once /robot01/move \
  std_msgs/msg/String "{data: 'forward'}"
```

Wait for the stop. Then try backward, left, right or stop.



Instructor note: Prepared robot firmware stops a directional movement after one second. Keep the motor-power switch accessible. A stop message can be delayed by the network; power switch is the immediate physical stop. Timed movement is not a measured distance. Use String direction commands, not the simulator Twist command.

## 36. Optional: a small Python change

SECOND BROWSER ROS TERMINAL

Run the LED example:

```bash
python examples/01_led.py
```

Change the timer from 1.0 to 0.5 seconds. Save and rerun.



Instructor note: Stop with Ctrl+C. Edit examples/01_led.py on the COMPUTER in the extracted kit; its folder is mounted in the container. Explain the publisher and timer without requiring classes/self from beginners. Explicitly send LED OFF afterwards; stopping the script can leave the last LED state. Further extension: combine sensor subscriber with LED publisher.

## 37. Mini-challenge and checkpoint

Show one virtual movement.
Show one real sensor change.
Send one LED command to your robot.

Explain: who publishes, who subscribes?
Where does ROS run? Where does MicroPython run?

Each partner demonstrates and explains one message.



Instructor note: Optional: short physical movement if time and setup allow. If Moodle work remains, reserve 16:15–16:50 for the remote laboratory and skip optional movement/Python challenge. Simulator has ideal pose, real RBussi has no encoders or measured pose.

## 38. End of class / next launch

COMPUTER TERMINAL

Send stop and LED OFF. Switch motor power off.

On the computer, shut down:

```bash
docker compose down

# Next time, in the same folder:
docker compose up -d
```

Start Docker first. Then reopen the browser desktop.

[Setup and exercises](https://github.com/spivakdm/rbussi-micropython/tree/main/ros2)

Instructor note: No new download or docker load is needed for the same installed version. ESP32 main.py starts on reset and waits for commands. To reconnect hardware, run robot-connect again. Save edited files before closing.
