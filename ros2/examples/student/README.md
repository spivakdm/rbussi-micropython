# Write your first ROS nodes

Use the prepared ROS image 0.2.8 or newer. This exercise controls the simulator only. No MQTT account or ESP32 connection is needed.

## Files and terminals

Download `RBussi-ROS-student-templates.zip` from the [0.2.8 release](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.2.8) and extract it into your existing kit folder, beside `compose.yaml`. You should then have `examples/student/01_sensor_subscriber.py`, and the other templates, inside that kit. If you use a fresh Git checkout, the files are already there.

Edit the files on your own computer in a text editor or in Thonny's local editor. Save them, then run them in the VNC terminal using the commands below. The kit shares its `examples` folder with `/course/examples` inside the container. You do not need to rebuild or restart the container. Run ROS code in the container, not on the MicroPython board.

Stop `sim-line-demo`, keyboard teleoperation and any previous movement program with Ctrl+C before starting your own controller. Keep only one movement publisher running. Open extra terminals with F8. Click inside a terminal before typing.

## 1. A subscriber (about 15 minutes)

In terminal A, start the track and sensors:

```sh
sim-line-track
```

In terminal B, inspect the interface:

```sh
ros2 topic info /sim/line
ros2 interface show std_msgs/msg/Int32MultiArray
ros2 topic echo /sim/line
```

The useful field is `data: [left, right]`. White = 0, black = 1. Press Ctrl+C to close the viewer. Complete TODO 1 in `01_sensor_subscriber.py`, save it and run:

```sh
python /course/examples/student/01_sensor_subscriber.py
```

Use `node.create_subscription(message_type, topic_name, callback, 10)`. The topic is `/sim/line`, the type is `Int32MultiArray`, and your callback is `show_sensors`. The final number sets the message queue depth.

Check: your program prints both values. Stop it with Ctrl+C. If you see nothing, first confirm terminal A still runs and `ros2 topic echo /sim/line` receives messages.

## 2. A publisher (about 15 minutes)

Complete the three TODOs in `02_velocity_publisher.py`:

- Create a publisher with `node.create_publisher(message_type, topic_name, 10)`.
- Set a small forward speed, such as 0.5.
- Send each message with `publisher.publish(command)`.

Use topic `/turtle1/cmd_vel` and message type `Twist`. `linear.x` is forward speed, `angular.z` is turn rate. These are simulator units per second and radians per second, not PWM percentages.

```sh
python /course/examples/student/02_velocity_publisher.py
```

Check: the robot moves for about three seconds, then stops. The supplied timer keeps publishing zero velocity afterwards. Press Ctrl+C to exit. Try a turn with `linear.x = 0.0` and `angular.z = 0.5`, then explain which field you changed.

## 3. A subscriber and publisher in one node (about 25 minutes)

Stop the previous movement program. Stop and restart `sim-line-track` in terminal A to place the robot back on the route. Keep it running.

In `03_line_follower.py`, complete only `choose_motion(left, right)`:

| Left | Right | Action | Return forward speed, turn rate |
|---:|---:|---|---|
| 0 | 0 | Straight | `0.9, 0.0` |
| 1 | 0 | Left | `0.5, 1.8` |
| 0 | 1 | Right | `0.5, -1.8` |
| 1 | 1 | Stop | `0.0, 0.0` |

Use `if/elif/else`. Start with these values, then change one at a time.

```sh
python /course/examples/student/03_line_follower.py
```

Check: complete one full lap. Cyan sensor dots mean 0, red dots mean 1. Explain why a positive turn rate turns left.

The starter already receives sensor messages and publishes at 20 Hz. It sends zero velocity if readings stop for 0.5 seconds. Leave that check in place. Both-white also occurs when the line is completely lost; this controller depends on starting on the track and staying near it. Before completing the TODO, the template commands zero speed.

## 4. Explain your node (about 10 minutes)

While your follower runs, use another terminal:

```sh
ros2 node info /student_line_follower
ros2 topic info /sim/line
ros2 topic info /turtle1/cmd_vel
ros2 run rqt_graph rqt_graph
```

Select Nodes/Topics (all) and refresh in rqt_graph. Identify your node's input and output. Ignore internal topics such as `/rosout` for this exercise.

Show your partner where a message arrives, where a decision is made and where a command is sent. Then stop the track publisher: the robot should stop automatically. Restart the track and follower for another attempt.

Ctrl+C stops each program. Allow roughly one second for Turtlesim to stop after closing a movement program. If the map covers the terminal, use Alt+Tab or right-click the desktop and use Windows. Minimized windows are in that same menu.
