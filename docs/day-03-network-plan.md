# Day 3 — Sound, Wi-Fi and MQTT

Metropolia ICT Summer School · Introduction to Mobile Robotics with a Remote Laboratory.

Wednesday 14 October 2026, 13:00–17:00. Working teaching sequence based on the instructor's supplied MQTT access file. This networking day replaces the earlier Day 3 line-control block; the subsequent ROS 2 days remain under discussion.

## Provided server and account structure

| Item | Provided value |
|---|---|
| Broker | `mqtt.ondroid.org` |
| Port | `8883` |
| Transport | MQTT over TLS, not a WebSocket endpoint |
| Student accounts | 20 separate accounts |
| Robot namespaces | `edu-2026-10/robot01` through `edu-2026-10/robot20` |
| Client IDs | Separate ESP32 and computer client IDs in each account row |
| Account activation | Instructor reports accounts activated; original CSV still says `PENDING` |

Credentials are kept in the instructor's local `teacher-access.csv`, which is excluded from Git and from the explicit student-ZIP file list. Give each student only their own account row. The CSV is not part of the public teaching materials.

The provided `cmd/#` and `telemetry/#` strings are subscription/permission filters. Publish to a concrete topic, never to a topic containing `#` or `+`. Use the exact host, username and assigned client IDs from the student's account row. A computer and ESP32 must not share a client ID.

## Connectivity check, 13 October 2026

Initial checks reached the broker over verified TLS, but login returned MQTT CONNACK code 5 while accounts were not yet activated.

After the instructor reported activation, the first account (`robot01`) was checked again from the instructor computer:

- TLS certificate verification succeeded with the computer's normal CA trust store.
- Login with the supplied computer client ID was accepted.
- A second login with the supplied ESP32 client ID was accepted.
- The computer client subscribed to `edu-2026-10/robot01/telemetry/connection-test`.
- The ESP32-identity test client published a unique, non-retained QoS 0 test message to that topic; the computer client received the matching topic and payload.
- Both clients disconnected cleanly. No messages were published to command or status topics.

The new computer terminal client also passed a telemetry receive check with the supplied CA on 13 October; its desktop test publisher connected using TLS 1.2. No commands/status messages were published in that check.

Both test clients actually ran on the instructor computer. This confirms the first account's two-client login and telemetry exchange from the tested Wi-Fi; it does not establish actual ESP32 connectivity, classroom Wi-Fi access, command-topic permissions or activation of the remaining 19 accounts. The original CSV activation column is now stale relative to the instructor's update.

Keep TLS verification enabled. A successful desktop TLS check is not proof that the ESP32 has the required CA certificate, clock setup and MQTT client configuration; those need their own test.

## Proposed application topics

The following are lesson payloads to implement and rehearse; they are not a claim that a robot application is already listening.

| Purpose for robot01 | Concrete topic | Example payload |
|---|---|---|
| Sensor telemetry | `edu-2026-10/robot01/telemetry/line` | `{"left":0,"right":1}` |
| LED command | `edu-2026-10/robot01/cmd/led` | `ON` or `OFF` |
| Sound command | `edu-2026-10/robot01/cmd/beep` | `{"frequency":2000,"duration_ms":200}` |
| Device status | `edu-2026-10/robot01/status` | `online` or `offline` |

ESP32 publishes telemetry and status, and subscribes to its command filter. The computer publishes commands and subscribes to its telemetry filter and status topic. These permission directions must be checked against the broker's actual ACL; the CSV column names alone do not prove that the permissions are active.

Use the matching prefix and assigned client IDs for every student. Start command messages without retention so reconnecting does not replay an earlier LED/sound command unexpectedly. Explain retained state separately as an optional topic.

## Schedule

| Time | Activity | Evidence |
|---|---|---|
| 13:00–13:15 | Demonstration: sensor, network message, command and sound | Students identify input, transport and output |
| 13:15–14:00 | Passive piezo PWM: frequency, fill ratio, `beep()` and a melody with `for` | Compare pitch and sound at fixed/changed parameters |
| 14:00–14:20 | ESP32 Wi-Fi connection | Print connection state and IP address |
| 14:20–14:35 | Break | |
| 14:35–15:00 | MQTT broker, client, topic, publish and subscribe | Send `hello` to an assigned concrete telemetry topic |
| 15:00–15:35 | Send line-sensor readings | Receive left/right values on the computer, then publish only on changes |
| 15:35–15:50 | Break | |
| 15:50–16:30 | Receive LED and sound commands | Only the intended robot responds |
| 16:30–16:50 | Combine periodic reading and command handling | Telemetry and commands work together |
| 16:50–17:00 | Checkpoint and save | Explain publisher/subscriber roles and save code |

This lesson does not require a new ESP32 firmware image: use the current MicroPython build plus a suitable MQTT client package. No new robot settings library is needed; pins can remain in each exercise as in Day 2. Keep account credentials in local private configuration, not in source uploaded to the public repository.

GPIO26/D2 was proposed for the external LED and can be used for a piezo in a separate exercise only if free. For simultaneous LED and piezo operation, use the built-in LED on GPIO2 and a verified free output for the piezo. Confirm the buzzer type and its electrical requirements before choosing its connection circuit.

## Learning sequence

The end-of-day demonstration is: a student sees their own robot's sensor readings on the computer, sends an LED command, and requests a short sound. Keep the network exercises stationary with motor power off; movement over MQTT is outside this day's core scope.

### Before students arrive

- Rehearse the entire sequence on an actual ESP32 on the classroom Wi-Fi, including TLS and command-topic permissions. Desktop broker tests alone are insufficient.
- Check the remaining accounts and distribute only each student's own credentials, topic prefix and two client IDs.
- Prepare one MQTT client on the computer side that supports TLS/TCP port 8883. Provide OS-specific setup instructions or preconfigured lab access; a browser-only client needs an additional WebSocket endpoint/backend.
- Prepare the MicroPython MQTT package, CA trust material and any clock setup required for certificate verification. Give students a tested connection template; building TLS/MQTT plumbing is not the learning objective.
- Verify the passive piezo model and its connection circuit. Reserve a free output; use GPIO2 for the built-in LED and, if electrically suitable and free, GPIO26 for the piezo.
- Keep passwords out of public code, screenshots, slides and class-wide files. Student credentials belong in local private configuration; pins remain directly in the exercises.

The ten programs are available in [Day 3 examples](../examples/day03/README.md), with upload instructions, a private settings template, pinned MQTT/time dependencies and a computer-side terminal client. Host checks do not replace the required ESP32/classroom-network rehearsal.

### 13:00–13:15 — Goal and demonstration

Show a change from white to black, its message arriving on the computer, and an LED/sound command returning to the robot. If the physical network rehearsal has not passed, demonstrate the verified components separately and explain the remaining connection step.

Ask students to identify the sensor, decision, communication channel and output. Introduce the final task before the terminology.

Result: students can describe what they will build.

### 13:15–13:30 — Exercise 1: one sound

Explain passive versus active buzzers. Use the passive piezo for frequency experiments. Start PWM at 50% fill, generate a short 2000 Hz tone, then stop and release PWM.

Students identify the output GPIO, frequency, fill ratio and duration. Keep the motor battery off. Stagger sound tests between groups so changes can be heard.

Result: a short tone that ends predictably.

### 13:30–13:45 — Exercise 2: frequency and fill ratio

At 50% fill, compare 500, 1000, 2000 and 4000 Hz. Then keep 2000 Hz and compare 10%, 25% and 50% fill. Change one parameter at a time.

Explain frequency in Hz, period, and the distinction between fill ratio and inverse duty ratio (Russian skvazhnost). Do not present fill ratio as a linear loudness control; students describe changes in pitch, loudness and timbre. Continuous HIGH at 100% does not generate a sustained alternating tone in a passive piezo.

Result: a small table of settings and observations.

### 13:45–14:00 — Exercise 3: a beep function and sequence

Students write `beep(frequency, duration_ms)`, then use a list of frequencies and a `for` loop to make a three-note sequence. The function is local to the exercise, not a new library.

Discuss why the same function will later be useful in an MQTT callback. The first melody can use short blocking delays; revisit their effect when combining tasks.

Result: a reusable function with clear parameters.

### 14:00–14:20 — Exercise 4: connect to Wi-Fi

Use a supplied connection template and the verified 2.4 GHz network. Students enter local private network settings, connect, and print connection status and the assigned IP address in Thonny.

Explain that joining an access point and receiving an IP do not by themselves prove the MQTT server is reachable. Give the connection attempt a timeout and useful diagnostic messages; this startup timeout is separate from the continuous Day 2 movement loops.

Result: each ESP32 shows a connected state and an IP address. No firmware replacement is expected.

### 14:20–14:35 — Break

Use a separate instructor support station for unresolved connections; do not spend the next plenary explanation debugging one laptop.

### 14:35–14:45 — MQTT roles and student setup

Explain broker, client, topic, publish, subscribe and payload with the class architecture. MQTT topics are application addresses, not GPIO pins or executable functions.

Assign each student their robot number and account. The computer uses the supplied PC client ID; ESP32 uses its different supplied client ID. Show the student's concrete topic and the subscription filter separately. Explain why `#` can appear in a subscription but not in a published topic.

Result: the computer client is connected and subscribed to the student's telemetry namespace.

### 14:45–15:00 — Exercise 5: send hello

Start the supplied ESP32 MQTT/TLS template. Publish `hello` to a concrete topic such as `edu-2026-10/robot01/telemetry/hello`. Students receive it on the computer.

Use a small payload before introducing sensor readings or JSON. Follow the first message through the complete path and distinguish Wi-Fi connected, MQTT authenticated and message delivered.

Result: the first ESP32-to-computer message.

### 15:00–15:15 — Exercise 6: send sensor readings

Read GPIO34 and GPIO35 and publish a JSON object such as `{"left":0,"right":1}` to the assigned `/telemetry/line` topic. Begin at a modest rate, for example once every 500 ms.

Students move black/white paper beneath each sensor and compare local Shell output with the received message. Explain JSON keys and values using the two familiar readings.

Result: remote observation of both sensors without driving the robot.

### 15:15–15:35 — Exercise 7: publish only when something changes

Save the previous left/right state and compare it with the new state. Publish only after a change. Optional: add a periodic heartbeat so a quiet sensor does not look like a disconnected device.

Ask students to compare message counts while holding the paper still and while moving it. This gives previous-state variables a practical purpose.

Result: fewer repeated messages without losing changes.

### 15:35–15:50 — Break

### 15:50–16:10 — Exercise 8: control the built-in LED

Subscribe on ESP32 to the assigned `/cmd/led` topic. Use explicit `if/elif/else`: `ON` sets the LED high, `OFF` sets it low, and other payloads produce a diagnostic message without changing the output.

Publish commands from the computer without retention. Start with the familiar LED before adding sound. Explain bytes/text conversion in the supplied callback only to the depth needed for the task.

Result: each student's command affects only their own robot's LED.

### 16:10–16:30 — Exercise 9: request a sound

Reuse `beep()` for a message on `/cmd/beep`, with proposed JSON fields `frequency` and `duration_ms`. Check that both fields are sensible numbers and within the teacher-selected lesson limits before driving the piezo. Reject malformed messages without terminating the whole program.

For the first version, keep sounds short, for example 200 ms. Discuss why a long `sleep()` in the callback delays reading sensors and handling the next command. A nonblocking sound state is an optional extension, not a prerequisite for everyone.

Result: a network command selects a short audible tone.

### 16:30–16:50 — Exercise 10: combine the system

Combine sensor telemetry with command handling in one `while True` loop. The supplied template should regularly poll/process MQTT messages, read sensors and decide when to publish. Do not add a 500 ms blocking sleep after every iteration just because telemetry is sent every 500 ms; use elapsed time for publishing while keeping the loop responsive.

Each student demonstrates: change a surface, receive a sensor message, send LED ON/OFF, then request a short beep. Work with a partner who observes the output and explains the message direction.

Result: a small connected-robot application with input, communication and output.

### 16:50–17:00 — Checkpoint

Save code locally and preserve private credentials separately. Each student answers:

1. Who publishes the sensor message, and who subscribes?
2. Which concrete topic controls my LED?
3. Why do the ESP32 and computer need different client IDs?
4. What happens if a callback blocks for several seconds?

Minimum completion: one telemetry message and one LED command on the actual ESP32. Sound and change-only publishing extend that baseline. Note unresolved hardware/network issues without substituting a successful desktop-only test for an ESP32 result.

## Contingencies and scope

If piezos are unavailable, preserve the programming sequence using built-in/external LED output, with PWM dimming as a short demonstration; frequency-to-pitch exercises wait for passive piezos. If networking fails, use the local sensor-driven LED and sound programs, then revisit the prepared remote-lab sensor/line tasks. Do not disable TLS verification to make a failed connection appear successful.

This day does not contain a dedicated remote-laboratory block and replaces its former Day 3 slot. Keep any required remaining remote assignments visible in the overall schedule; do not silently turn them into homework.

ROS 2 can reuse the same telemetry/command concepts on Days 4–5. A bridge, simulator and student ROS environment still have to be prepared; this lesson alone does not provide them.

## Remaining rehearsal

1. Check the remaining student accounts with their assigned credentials; the first account has passed.
2. Verify command-topic permissions and the other accounts' telemetry exchange; the first account's telemetry round trip has passed.
3. Check status-topic permissions and delivery.
4. Confirm a second student namespace stays independent and that the server has capacity for ESP32 and computer connections for the whole group.
5. Connect the ESP32 on the actual classroom Wi-Fi and verify TLS, telemetry and LED commands.
6. Repeat a disconnect/reconnect test before distributing the final examples.

The connection check should be performed on the actual teaching network; a successful connection from another Wi-Fi does not establish classroom access. Confirm the ESP32-compatible 2.4 GHz network and its authentication method. A browser-only MQTT client requires a separate WebSocket endpoint or a backend; the supplied TLS/TCP port is not sufficient for direct browser connections.

## Connection to Days 4–5

A later ROS 2 node on the computer can bridge these MQTT messages to ROS topics. The MQTT broker remains the communication service for the ESP32. It is not a ROS server, and the account file contains MQTT access, not Linux/ROS desktop accounts.

The bridge, student ROS environment and robot simulator still need implementation/preparation. Reuse the same per-robot namespace so the course progresses from MQTT messages to ROS publishers/subscribers without reflashing the MicroPython robots.

## References

- [MicroPython ESP32 networking](https://docs.micropython.org/en/v1.29.0/esp32/quickref.html#networking).
- [MicroPython MQTT client package](https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple).
- [Mosquitto subscriber client documentation](https://mosquitto.org/man/mosquitto_sub-1.html).
- Broker parameters, account structure and pending activation come from the instructor-supplied local CSV. Connectivity results above were measured from the instructor computer, without exposing passwords.
