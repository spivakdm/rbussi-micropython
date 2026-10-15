# ROS 2 + RBussi: student setup

ROS 2 runs on your computer in a container. The ESP32 keeps MicroPython and exchanges commands and sensor readings through the existing MQTT broker. No ROS installation on your host OS and no ESP32 reflashing are needed if MicroPython is already installed.

```text
ROS nodes ↔ Python MQTT bridge ↔ mqtt.ondroid.org ↔ ESP32 MicroPython
```

Instructor: see the [beginner-friendly four-hour lesson plan](LESSON_PLAN.md).

## 1. Download

Open the [ROS classroom release](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.2.2). Download:

- `RBussi-ROS-kit-v0.2.2.zip`: robot files, configuration templates and exercises. Extract it before continuing.
- ONE ready-built Docker image from [container release 0.2.1](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.2.1): `rbussi-ros-0.2.1-amd64.tar.gz` for Intel/AMD computers, including Intel Macs; `rbussi-ros-0.2.1-arm64.tar.gz` for Apple Silicon Macs or ARM64 Linux.

Keep the image archive compressed: `docker load` reads it directly. The two archives contain the same image name, built for different processors. The release uses downloadable images rather than a container registry: use `docker load`, **not `docker compose pull`**.

### Updating an existing installation

Kit 0.2.2 fixes MQTT subscription timeouts on the ESP32. Upload the new `robot/main.py` as `/main.py` and reset the board. Keep your private settings. Confirm that `robot.py`, `drive_command.py`, `robot_mqtt.py` and the `umqtt` folder are also present.

The Docker image remains 0.2.1; no container download or rebuild is needed.

## 2. Install Docker

| Computer | Install |
|---|---|
| Windows | [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), using Linux containers and the WSL 2 backend. Complete any required WSL/virtualization setup and restart. |
| macOS | [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/) for your processor. Start Docker Desktop after installing. |
| Linux | Docker Engine plus the Compose plugin; follow the [Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/) or the matching distribution guide. |

In PowerShell (Windows) or Terminal (macOS/Linux), check:

```sh
docker version
docker compose version
```

`docker version` must show a working Server, not only Client. Windows ARM is not part of the rehearsed setup. No GUI forwarding, USB forwarding, host networking or Docker privileged mode is needed for this kit.

## 3. Start with simulation

Load the matching image using step 6, run `docker compose up -d`, and open **http://localhost:6080/vnc.html?autoconnect=true&resize=scale**. Turtlesim and a terminal start automatically. Follow [SIMULATOR.md](SIMULATOR.md).

You may skip robot setup and `settings.env` for this first part. Docker Compose 2.24 or newer is required for the optional settings file. The simulator works without MQTT; the real-robot bridge is deliberately not started automatically.

## 4. Prepare the ESP32 in Thonny

Keep motor power off while uploading. Back up an existing `main.py` and your private settings before replacing files.

1. In the extracted kit's `robot` folder, copy `network_secrets.example.py` to `network_secrets.py`.
2. Enter ordinary 2.4 GHz Wi-Fi credentials and your assigned MQTT account. Use TCP port **1883**. Use the ESP32 client ID on the board.
3. Check `TOPIC_PREFIX`: for robot01 it is exactly `edu-2026-10/robot01` — no leading `/`, no `/status`, no trailing `/`.
4. Upload these files to the board root using **View → Files → Upload to /**:

```text
/
  main.py
  robot.py
  drive_command.py
  robot_mqtt.py
  network_secrets.py
  umqtt/
    __init__.py
    simple.py
```

The release ZIP contains all these code files. When using the Git source instead, `robot.py` is at the repository root and `umqtt` is in `examples/day03/umqtt`.

Restart with the board RESET button or reconnect power. `main.py` runs automatically. In Thonny Shell, look for `Wi-Fi connected` and `READY: edu-2026-10/robot01`. The robot stays stopped until it receives a command. GPIO2 is the built-in LED; GPIO26/D2 is the verified passive piezo; A3/GPIO34 and A2/GPIO35 are the line sensors (white 0, black 1).

If Wi-Fi or MQTT fails, the program stops the motors and exits. Fix the settings and restart the board. The first version does not automatically reconnect. To disable automatic startup, stop with Ctrl+C in Thonny and rename or remove `main.py` on the board.

## 5. Configure the computer for the real robot

In the extracted kit folder, copy `settings.env.example` to `settings.env`. Open it in a text editor and enter your account. For robot01:

```text
MQTT_HOST=mqtt.ondroid.org
MQTT_PORT=1883
MQTT_USER=YOUR_ASSIGNED_USERNAME
MQTT_PASSWORD=YOUR_ASSIGNED_PASSWORD
MQTT_PREFIX=edu-2026-10/robot01
MQTT_CLIENT_ID=edu-2026-10-robot01-pc
ROBOT_NAME=robot01
```

Replace every robot number consistently. For passwords containing `$` or `#`, enclose the complete value in single quotes in `settings.env`. Do not publish either private settings file. TCP/1883 carries messages and credentials without TLS encryption.

Disconnect MQTTX/MQTT Explorer if it uses the same PC client ID. Two simultaneous clients with the same ID disconnect one another.

## 6. Load and start

Open a terminal **in the extracted kit folder** (the folder containing `compose.yaml`). Put the downloaded image archive in that folder, or pass its full path.

Intel/AMD:

```sh
docker load -i rbussi-ros-0.2.1-amd64.tar.gz
```

Apple Silicon / ARM64:

```sh
docker load -i rbussi-ros-0.2.1-arm64.tar.gz
```

Then, on all operating systems:

```sh
docker compose up -d
docker compose logs --tail 20
```

Open the browser desktop at **http://localhost:6080/vnc.html?autoconnect=true&resize=scale**. It shows a virtual RBussi and a ROS terminal. To use a terminal outside the browser instead:

```sh
docker compose exec ros bash
```

ROS is already sourced in this interactive shell. For the physical robot, enter `robot-connect` and look for `MQTT connected: edu-2026-10/robot01`. Keep that terminal open while using the robot. This is an explicit connection step; no MQTT connection occurs just by opening Turtlesim.

Open a second terminal using `ros-terminal` in the browser, or another `docker compose exec ros bash` on your computer. Physical-robot commands below run **inside** it:

```sh
ros2 node list
ros2 topic list
ros2 topic echo /robot01/line
```

Use your own robot number. Ctrl+C stops the topic viewer, not the robot application or bridge. Open a second host terminal and run `docker compose exec ros bash` for a second ROS shell. All nodes run inside the same container; no ROS discovery between student laptops is required.

## 7. First real-robot commands

LED (inside the ROS shell):

```sh
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'ON'}"
ros2 topic pub --once /robot01/led std_msgs/msg/String "{data: 'OFF'}"
```

Lift the wheels, enable motor power, and send one movement:

```sh
ros2 topic pub --once /robot01/move std_msgs/msg/String "{data: 'forward'}"
```

Forward and backward run for one second at 40% PWM. Left and right turn on the spot for 400 ms at 35% PWM. They are timed turns, not measured angles. Wait for a movement to finish before repeating it.

```sh
ros2 topic pub --once /robot01/move std_msgs/msg/String "{data: 'stop'}"
```

The stop command is handled during motion; the application does not sleep for the movement duration. Use the physical motor-power switch when an immediate stop is needed: Wi-Fi/MQTT is not a guaranteed emergency-stop channel.

## 8. Exercises and shutdown

Start with [SIMULATOR.md](SIMULATOR.md), then continue with [EXERCISES.md](EXERCISES.md) for the physical robot. The examples directory is mounted from your computer into the container. Edit these files on your computer, then run them inside the ROS shell; your edits survive container removal.

Before finishing, send `stop`, switch motor power off, and leave the ROS shell with `exit`. In the host terminal:

```sh
docker compose down
```

The ESP32 still runs independently until powered off or stopped in Thonny. After changing `settings.env`, apply it with `docker compose up -d --force-recreate`. Restart a failed bridge by running `robot-connect` again. Restarting the container also closes the bridge; open it explicitly again when ready.

## Troubleshooting

- **No ROS messages:** check board `READY`, correct prefix, bridge logs and matching robot number. `main.py` must be running; Thonny Stop interrupts it.
- **No Docker image:** complete `docker load` for the correct architecture first. To build from source instead, run `docker compose build` in the source `ros2` directory, then `docker compose up -d`.
- **Login rejected / disconnects:** check exact account credentials and PC/ESP32 IDs. Close another PC client with the same ID.
- **No movement:** check motor power and charge; sensor telemetry only proves the ESP32 is alive.
- **No ROS CLI discovery:** run all ROS commands inside `docker compose exec ros bash`, not in a host terminal or separate Docker container.
- **Fresh commands only:** command retention must be off. The board rejects retained commands. ROS command publishers use volatile QoS. The bridge drops commands while MQTT is offline.

## Limits and verification

Speed values are PWM percentages, not m/s. `/state` reports commanded outputs, not measured wheel velocity or odometry. The kit includes standard Turtlesim with RBussi artwork. There is no physical-robot odometry, localization, SLAM or `cmd_vel` mapping. Simulation controls do not command the real robot.

Wheel requests are limited to ±60% PWM and at most 1000 ms. Without a fresh request, the local timer stops the motors. Invalid commands also stop them. MQTT packet reads have a bounded deadline; errors close motor outputs. This is a software timeout, not a hard real-time guarantee: scheduling and network writes can delay processing. Delayed live commands can still arrive; do not repeatedly queue commands.

On 15 October 2026, Linux/amd64 + physical ESP32 robot19 passed sensor telemetry, LED ON/OFF, forward with automatic stop and a separate stop during motion. The instructor observed wheel movement and stopping. State telemetry showed automatic stopping roughly 0.86 seconds after the first received moving state, and an explicit-stop response around 0.22 seconds; these are network observations, not precision timing measurements. Windows/macOS installation and other student accounts still need classroom rehearsal. Version 0.2.1 adds the browser desktop and RBussi Turtlesim artwork. Local tests passed browser keyboard input, ROS velocity commands, reset, sprite replacement and MQTT remaining off by default. See release assets for available built architectures.

Sources: [official ROS Docker image](https://hub.docker.com/_/ros), [Paho MQTT client](https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html). The upstream `umqtt` source and license are included in the kit; it remains unmodified. `robot_mqtt.py` supplies bounded packet reads and retained-message filtering for this application.
