# First ROS 2 exercises with RBussi

Complete [the Turtlesim introduction](SIMULATOR.md) first. For the exercises below, configure the physical robot, run `robot-connect` in one terminal, and keep it running.

Run ROS commands inside `docker compose exec ros bash`. Replace `robot01` with your assigned number. Work with wheels lifted before trying any floor movement.

## 1. Find the nodes and topics — 10 minutes

```sh
ros2 node list
ros2 topic list
ros2 topic info /robot01/line
ros2 topic type /robot01/line
```

Find `mqtt_bridge`. Which topic contains sensor data? Which carries movement commands? ROS topics and MQTT topics are different channels connected by the bridge.

## 2. Read real sensors — 10 minutes

```sh
ros2 topic echo /robot01/line
```

Move white paper and a black stripe below each sensor. The array is `[left, right]`. White = 0, black = 1. Stop the viewer with Ctrl+C.

Run the subscriber example:

```sh
python examples/02_read_line.py
```

Identify the callback and subscription. Add a printed message when only the left sensor sees black. No motor command is needed.

## 3. Publish LED commands — 10 minutes

```sh
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'ON'}"
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'OFF'}"
```

Run `python examples/01_led.py`. Change the timer from 1.0 to 0.5 seconds. Explain the publisher and timer callback. Ctrl+C ends blinking; explicitly send OFF afterwards because the LED may retain its last state.

## 4. Move, turn and stop — 15 minutes

Lift wheels and enable motor power. Send one `forward`, wait for stopping, then try `backward`, `left` and `right`:

```sh
ros2 topic pub --once /robot01/move std_msgs/msg/String "{data: 'forward'}"
```

Open a second ROS shell and observe:

```sh
ros2 topic echo /robot01/state
```

Send `stop` during a movement. Run `python examples/03_drive.py`; change the string to another valid direction. Explain why the publisher waits for a subscriber before sending once.

## 5. Control each wheel — optional, 15 minutes

```sh
ros2 topic pub --once /robot01/wheels std_msgs/msg/String '{data: "{\"left\":30,\"right\":40,\"duration_ms\":500}"}'
```

The inner JSON is a String message. Adjust left/right PWM independently. Allowed integers: wheel commands -60..60, duration 50..1000 ms. This is not a linear/angular velocity command. Compare equal and unequal wheel settings.

## 6. Request sound — optional, 10 minutes

With the verified passive piezo on GPIO26:

```sh
ros2 topic pub --once /robot01/beep std_msgs/msg/String '{data: "{\"frequency\":2000,\"duration_ms\":200}"}'
```

While a tone plays, inspect the sensor stream. The robot uses a deadline instead of a long blocking sleep.

## 7. A sensor-to-LED ROS node — optional, 20 minutes

Combine the subscriber from exercise 2 with the publisher from exercise 3. If both sensor values are 1, publish ON to the LED; otherwise publish OFF. Keep motor power off. Identify the complete path: ESP32 sensor → MQTT → ROS subscriber → ROS publisher → MQTT → ESP32 LED.

## Checkpoint

Explain node, topic, publisher, subscriber and callback. Demonstrate one real sensor change and one command. Explain why the ROS and MQTT topic names differ and why commanded PWM is not measured speed. End with `stop`, LED OFF and motor power off.
