# Meet RBussi in Turtlesim

Start with simulation. No robot, Wi-Fi credentials or MQTT account is needed. The real robot receives no commands from these exercises.

## Open the classroom desktop

After loading the 0.2.1 image and running `docker compose up -d`, open:

**http://localhost:6080/vnc.html?autoconnect=true&resize=scale**

The left window is Turtlesim; the terminal is on the right. The red/pink bus is a simplified top view based on the instructor's robot drawings. At startup the front points right.

## 1. Drive with arrow keys

Click inside the terminal, type this command and press Enter:

```sh
ros2 run turtlesim turtle_teleop_key
```

Keep keyboard focus in the **terminal**, not the simulator window. Use Up/Down to move forward/backward and Left/Right to turn. Stop sending keys and motion stops after the simulator's short command timeout. Ctrl+C ends keyboard control.

Ask: which end is the front? Does the bus follow the direction it faces?

## 2. Find the channels

After Ctrl+C:

```sh
ros2 node list
ros2 topic list
ros2 topic echo /turtle1/pose
```

The standard names remain `turtle1` and `turtlesim` so normal ROS tutorials still apply. `x` and `y` are position; `theta` is heading in radians. Ctrl+C closes the viewer. To open another terminal, type `ros-terminal`, or use `docker compose exec ros bash` in a second terminal on your computer.

## 3. Send one velocity message

```sh
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.0}}"
```

This requests forward velocity, not a one-metre destination. Turtlesim stops roughly one second after its last velocity message. Then try turning:

```sh
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 1.0}}"
```

Combine nonzero linear and angular values to draw an arc. Do not introduce all fields of Twist at once: today, `linear.x` means forward/backward and `angular.z` means turn.

## 4. Reset the drawing

```sh
ros2 service call /reset std_srvs/srv/Empty "{}"
```

Treat this as a supplied reset command; services can be studied later. It clears the trail and resets the simulated bus. The RBussi appearance remains after reset or spawning another turtle.

## 5. Move to the real robot

Follow the robot setup in [README.md](README.md), recreate the container after adding `settings.env`, and run `robot-connect` in a dedicated terminal. Keep that terminal open. Open another terminal with `ros-terminal` or `docker compose exec ros bash` for commands.

| Simulation | Real RBussi through our bridge |
|---|---|
| `/turtle1/cmd_vel`, message type Twist | `/robot01/move`, message type String |
| `linear.x` and `angular.z` | `forward`, `backward`, `left`, `right`, `stop` |
| `/turtle1/pose` | `/robot01/line` and `/robot01/state` |
| Ideal simulated pose | Two line sensors and commanded outputs; no measured pose |

Replace robot01 with your number. These are separate controls: typing an arrow in turtle teleop never moves the real robot. There is no automatic forwarding from `/turtle1/cmd_vel` to MQTT. Keep motor power off while exploring simulation.

## What the picture changes

The sprite changes appearance only. This is standard Turtlesim, not a physical RBussi model: no wheel slip, real dimensions, line-sensor simulation or obstacle collision model has been added. The drawn trail is a visual aid, not a line-following track. The stock `color_sensor` samples the simulator canvas; it is not our pair of D0 sensors.

The original 45 × 45 image canvas is preserved to keep the stock coordinate scale. Body proportions are based on `top.dxf` (200 × 90 mm); roof details and visible wheels are illustrative. See [artwork notes](assets/README.md).

## Browser troubleshooting

- Start Docker and the container before opening the URL. Initial desktop startup may take several seconds.
- If arrows do nothing, click the terminal running `turtle_teleop_key`; clicking the bus window does not send commands.
- If the bus window closes, it restarts automatically. Use `/reset` to clear the drawing.
- The browser desktop is exposed only on this computer's loopback address. Do not change the port mapping to expose it on a public network; there is no desktop password in this classroom configuration.
- If the browser view is too small, maximize the browser and hide the noVNC side panel. No XQuartz or host X11 setup is needed.

Sources: [ROS Turtlesim implementation](https://github.com/ros/ros_tutorials/tree/jazzy/turtlesim), [noVNC browser client](https://github.com/novnc/noVNC).

### Keyboard focus

Click inside the terminal before typing. Clicking the simulator moves keyboard focus away from the terminal. If keyboard control is running, press Ctrl+C before entering another shell command.
