# Instructor reference: student ROS templates

Allow about 65 minutes before connecting the physical robot. Students edit their own copies of `examples/student`. The downloadable student ZIP omits this answer sheet. Existing full examples remain available in the repository for reference.

## Task 1

Replace `subscription = None` with:

```python
subscription = node.create_subscription(
    Int32MultiArray, '/sim/line', show_sensors, 10)
```

Ask: who calls `show_sensors`? A message arrival causes the ROS executor to invoke the callback while `rclpy.spin(node)` runs.

## Task 2

Replace `publisher = None` with:

```python
publisher = node.create_publisher(Twist, '/turtle1/cmd_vel', 10)
```

Set the nonzero movement speed to `command.linear.x = 0.5`. Replace the `pass` inside `if publisher is not None` with `publisher.publish(command)`. The existing three-second limit then publishes zero velocity, while the program keeps running until Ctrl+C.

Ask: why does zero velocity stop the robot even though the node is still running?

## Task 3

```python
def choose_motion(left, right):
    if left == 0 and right == 0:
        return 0.9, 0.0
    elif left == 1 and right == 0:
        return 0.5, 1.8
    elif left == 0 and right == 1:
        return 0.5, -1.8
    else:
        return 0.0, 0.0
```

Do not change the stale-data timer. Assess one lap, a correct explanation of input/output topic types, and the stop after the sensor publisher ends. The both-white ambiguity is an explicit limitation, not something solved by a larger turn rate.

Common issues: forgot to save; ran a local Python interpreter instead of the container; wrong topic spelling; still running teleop or the reference demo; restarted the track while the old controller was active. Stop movement publishers before repositioning the robot.

The physical robot still uses `/robot01/line` and String movement/wheel commands through MQTT. Do not simply rename the simulator's Twist output to a physical-robot topic: its command format and units differ.
