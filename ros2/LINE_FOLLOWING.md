# Two-sensor line following on the Riihimäki map

## Write your own ROS node

Before connecting the physical robot, use the [student templates](examples/student/README.md):
read the sensors, publish velocity, then complete a four-rule relay controller.
Download the separate `RBussi-ROS-student-templates.zip` from
[release 0.2.7](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.2.7)
and extract it beside your existing `compose.yaml`. No new image is needed.
Instructor answers: [solution sheet](teacher/STUDENT_SOLUTIONS.md).


This exercise controls the simulated RBussi only. It does not connect to MQTT or move a physical robot. Stop keyboard teleoperation before starting the follower: only one program should publish movement commands at a time.

## Quick demonstration

In the VNC terminal:

```sh
sim-line-demo
```

The robot starts on a closed black route along the road centres, including the large loop west of Hyria, and follows it. Ctrl+C stops the demonstration. To see the map more clearly, maximize its window; switch back to the terminal with Alt+Tab or the desktop Windows menu. The normal simulator does not start driving automatically.

## Exercise 1: read two sensors

In the first terminal:

```sh
sim-line-track
```

This draws the track, positions the robot at the start and publishes `/sim/line`. Open another terminal with F8:

```sh
python /course/examples/04_sim_line_reader.py
```

Readings are `[left, right]`, relative to the robot's forward arrow: white = 0, black = 1. Cyan dots show 0; red dots show 1. Each reading samples the centre of a dot. The sensors see only the new black route, not the background map, labels, robot sprite or trails. The white outline around the route makes it visible on the city artwork.

You can also inspect the ROS topic:

```sh
ros2 topic echo /sim/line
ros2 topic info /sim/line
```

Stop the reader with Ctrl+C. Optionally use `ros2 run turtlesim turtle_teleop_key` in this terminal to move slowly across the line while watching the readings in a third terminal. Stop teleoperation before running the follower.

## Exercise 2: follow the line

With `sim-line-track` still running, run:

```sh
python /course/examples/05_sim_line_follower.py
```

| Left | Right | Action |
|---:|---:|---|
| 0 | 0 | Forward |
| 1 | 0 | Turn left |
| 0 | 1 | Turn right |
| 1 | 1 | Stop |

The example's `steering()` function contains these four rules. `linear.x` is forward speed in simulator units per second; `angular.z` is turn rate in radians per second. Positive turn rate means left. These values are not motor PWM percentages.

The subscriber receives the readings. A timer publishes movement 20 times per second. If readings stop arriving for 0.5 seconds, it publishes zero velocity. Turtlesim also has its normal command timeout. Ctrl+C stops the example; allow up to about one second for Turtlesim's timeout if the ROS process shuts down before its final stop message is delivered.

## Exercise 3: change one setting

Change the straight speed (initially 0.9), then the turning speed (0.5) or turn rate (1.8). Test one change at a time. Can the robot complete a lap? Does it wobble more or leave the line?

Both-white is ambiguous: it means either that the line is between the sensors or that the robot has lost the line entirely. This simple controller assumes it starts correctly and stays close enough to the route. It does not magically locate a lost line. Both-black is deliberately treated as a stop condition in this exercise.

## Restart and return to ordinary Turtlesim

Stop the follower first, then stop `sim-line-track`. Restart the track to return the robot to its starting point. The route and dots disappear within about one second after the sensor node stops. Starting the track turns the drawing pen off; to restore the ordinary simulator and pen settings after stopping the exercise:

```sh
ros2 service call /reset std_srvs/srv/Empty '{}'
```

The map remains visible. Resizing the window does not change the route or sensor geometry.

## ROS connections

```text
/turtlesim ── /turtle1/pose ──> /sim_line_sensors
                                     │
                                /sim/line
                                     ↓
                             /sim_line_follower
                                     │
                             /turtle1/cmd_vel
                                     ↓
                                /turtlesim
```

`/sim/overlay` is a display-only JSON topic used internally to draw the route and dots. The follower reads only `/sim/line`: it does not receive the robot's pose or the track geometry. This is a digital teaching model, not an optical simulation of a physical infrared module.

The route is a separate teaching overlay. Rights to the underlying Riihimäki map remain with Robotx Oy; see [the map notice](assets/RIIHIMAKI-MAP-NOTICE.txt).
