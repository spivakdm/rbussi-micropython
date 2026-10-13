# Day 3 Draft — Sound, Wi-Fi and MQTT

Metropolia ICT Summer School · Introduction to Mobile Robotics with a Remote Laboratory.

Wednesday 14 October 2026, 13:00–17:00. This is a proposed networking lesson, based on the instructor's supplied MQTT access file. It replaces part of the earlier Day 3 line-control work if adopted.

## Provided server and account structure

| Item | Provided value |
|---|---|
| Broker | `mqtt.ondroid.org` |
| Port | `8883` |
| Transport | MQTT over TLS, not a WebSocket endpoint |
| Student accounts | 20 separate accounts |
| Robot namespaces | `edu-2026-10/robot01` through `edu-2026-10/robot20` |
| Client IDs | Separate ESP32 and computer client IDs in each account row |
| Account activation in the supplied file | All rows marked `PENDING` |

Credentials are kept in the instructor's local `teacher-access.csv`, which is excluded from Git and from the explicit student-ZIP file list. Give each student only their own account row. The CSV is not part of the public teaching materials.

The provided `cmd/#` and `telemetry/#` strings are subscription/permission filters. Publish to a concrete topic, never to a topic containing `#` or `+`. Use the exact host, username and assigned client IDs from the student's account row. A computer and ESP32 must not share a client ID.

## Connectivity check, 13 October 2026

From the instructor computer's current Wi-Fi:

- DNS resolved the broker.
- TCP connection to port 8883 succeeded.
- TLS certificate verification succeeded with the computer's normal CA trust store.
- MQTT 3.1.1 CONNECT for the first account, using its supplied computer client ID, returned CONNACK code 5: **Not authorized**.
- A diagnostic client ID also received code 5. No messages or motor commands were published.

This verifies network reachability from the tested computer only. It does not verify the classroom Wi-Fi, the ESP32 connection, or student publish/subscribe permissions. The instructor confirmed that the accounts have not yet been activated; defer further authentication and message-exchange tests until activation. Account activation/authorization must be resolved before an end-to-end classroom rehearsal. The other 19 logins have not been tested.

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

## Rehearsal after account activation

1. Verify the assigned login using the issued computer client ID.
2. Verify publish and subscribe on the assigned command and telemetry topics with two clients.
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
