"""Sensor telemetry + LED + nonblocking sound. No motor commands."""
from machine import Pin, PWM
from time import ticks_add
# JSON converts a Python dictionary to message text and back.
import json

# network controls the ESP32 Wi-Fi interface.
import network
# ssl provides TLS encryption and verification of the broker certificate.
import ssl
# ntptime sets the board clock from an Internet/local time server.
import ntptime
# Read your private settings file; do not put passwords in this example.
import network_secrets as settings
from time import sleep_ms, ticks_ms, ticks_diff, gmtime
# Use the supplied upstream MQTT client uploaded as umqtt/simple.py.
from umqtt.simple import MQTTClient

def connect_wifi():
    # Create the station interface: the ESP32 joins an existing access point.
    wlan = network.WLAN()
    # Enable the Wi-Fi radio before attempting a connection.
    wlan.active(True)
    # Reuse an existing connection when this program is run again.
    if not wlan.isconnected():
        # Start joining the network; receiving an IP address takes time.
        wlan.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)
    # Remember when the attempt began. ticks_ms() counts elapsed milliseconds.
    started = ticks_ms()
    # Wait for the network connection, but do not wait forever.
    while not wlan.isconnected():
        # ticks_diff handles the timer wrapping around; 15000 ms = 15 seconds.
        if ticks_diff(ticks_ms(), started) >= 15000:
            # Cancel the unsuccessful attempt before reporting the error.
            wlan.disconnect()
            raise OSError("Wi-Fi timeout: check 2.4 GHz, password and network access")
        # Pause briefly between checks instead of checking continuously.
        sleep_ms(250)
    # Print to Thonny Shell. The first ifconfig item is our local IP address.
    print("Wi-Fi connected; IP:", wlan.ifconfig()[0])
    # Return the connected interface if the caller wants to inspect it.
    return wlan


def make_client():
    # Supplied connection template: Wi-Fi, clock, CA verification, credentials.
    # First establish Wi-Fi; MQTT and NTP need network access.
    connect_wifi()
    # TLS checks certificate dates, so the board needs the actual UTC time.
    if settings.SYNC_NTP:
        # Choose the time server from the private configuration.
        ntptime.host = settings.NTP_HOST
        # Limit each NTP socket wait to three seconds (DNS may take longer).
        ntptime.timeout = 3
        # Try at most three times; attempt takes the values 0, 1 and 2.
        for attempt in range(3):
            try:
                # Request UTC time and update the ESP32 real-time clock (RTC).
                ntptime.settime()
                # A successful time update ends the retry loop.
                break
            except OSError:
                # After the third failed attempt, report the problem instead of disabling TLS.
                if attempt == 2:
                    raise OSError("NTP failed: set current UTC RTC; see README")
                sleep_ms(500)
    # Catch an obviously unset clock; this is not a full date-accuracy check.
    if gmtime()[0] < 2026:
        raise OSError("Set the board RTC to current UTC before TLS")
    # Create the TLS configuration for a client connecting to a server.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Require a certificate chain trusted by our CA; reject unverified servers.
    context.verify_mode = ssl.CERT_REQUIRED
    # Load the public root CA file from the ESP32 filesystem, not a client key.
    context.load_verify_locations(cafile=settings.CA_FILE)
    # Create the client object; the actual connection happens at client.connect().
    # The supplied MQTT client passes the broker hostname to TLS for verification.
    # Credentials/client ID use bytes (.encode()); keepalive is in seconds.
    return MQTTClient(
        settings.ESP32_CLIENT_ID.encode(), settings.MQTT_HOST,
        port=settings.MQTT_PORT, user=settings.MQTT_USER.encode(),
        password=settings.MQTT_PASSWORD.encode(), keepalive=60, ssl=context,
    )

# Use ESP32 GPIO numbers, not the Arduino-style A3/A2 labels.
LEFT_GPIO = 34   # A3; white=0, black=1.
RIGHT_GPIO = 35  # A2; confirm sides by covering one sensor at a time.
# Digital inputs read D0 as 0 or 1; these examples do not use ADC.
left = Pin(LEFT_GPIO, Pin.IN)
right = Pin(RIGHT_GPIO, Pin.IN)

# The built-in LED is active high: 1 = on, 0 = off.
BUILTIN_LED_GPIO = 2
PIEZO_GPIO = 26  # D2; confirm free pin and suitable passive piezo circuit.
line_topic = (settings.TOPIC_PREFIX + "/telemetry/line").encode()
led_topic = (settings.TOPIC_PREFIX + "/cmd/led").encode()
beep_topic = (settings.TOPIC_PREFIX + "/cmd/beep").encode()
# None means no tone is currently scheduled to stop.
beep_until = None

def read_beep(message):
    # Reject malformed JSON, missing fields, booleans and out-of-range values.
    try:
        # Parse the incoming JSON bytes into a Python value.
        data = json.loads(message)
        # Valid JSON could be a list or number; we specifically need an object.
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        # Missing keys return None, which will fail the integer check below.
        frequency = data.get("frequency")
        duration_ms = data.get("duration_ms")
        # Require actual integers; reject strings, decimals and JSON true/false.
        if type(frequency) is not int or type(duration_ms) is not int:
            raise ValueError("Use integer frequency and duration_ms")
        # Bound the pitch and duration before passing them to the hardware.
        if not 100 <= frequency <= 5000 or not 20 <= duration_ms <= 1000:
            raise ValueError("Use 100..5000 Hz and 20..1000 ms")
        # Return the two validated values for tuple unpacking by the caller.
        return frequency, duration_ms
    except (ValueError, TypeError):
        print("Ignored beep: expected integer frequency 100..5000, duration_ms 20..1000")
        # None means invalid command: leave the output unchanged and keep running.
        return None


# The MQTT library supplies topic and message as bytes, not ordinary strings.
def on_message(topic, message):
    # The callback updates the same deadline that the main loop checks.
    global beep_until
    # Check the topic first so the payload is interpreted for the correct device.
    if topic == led_topic:
        # Compare bytes with bytes; commands are case-sensitive.
        if message == b"ON":
            # Drive GPIO2 HIGH to turn the built-in LED on.
            led.value(1)
        # Only this exact command switches the LED off.
        elif message == b"OFF":
            # Drive GPIO2 LOW to turn the LED off.
            led.value(0)
        else:
            print("Ignored LED command: expected ON or OFF")
    elif topic == beep_topic:
        # Validate first; malformed commands must not start a tone.
        command = read_beep(message)
        if command is not None:
            # Unpack the validated pair into two clearly named variables.
            frequency, duration_ms = command
            # Select the requested pitch without pausing the main loop.
            sound.freq(frequency)
            # Start the tone at approximately 50% fill.
            sound.duty_u16(32768)
            # Store an end time, using ticks_add so timer wraparound is handled.
            beep_until = ticks_add(ticks_ms(), duration_ms)
            # A new valid command replaces the current tone; no sleep here.


# Prepare Wi-Fi, UTC time, verified TLS and our assigned MQTT identity.
client = make_client()
led = Pin(BUILTIN_LED_GPIO, Pin.OUT, value=0)
# Start the piezo output LOW, before attaching PWM.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
# Prepare PWM at 2000 Hz, initially silent with zero fill ratio.
sound = PWM(pin, freq=2000, duty_u16=0)
try:
    # Register the function MQTT calls when a subscribed message arrives.
    client.set_callback(on_message)
    # Connect to the broker and authenticate; initial socket timeout is 10 s.
    client.connect(timeout=10)
    # Ask the broker to deliver messages for our LED command topic.
    client.subscribe(led_topic)
    # Ask the broker to deliver messages for our sound command topic.
    client.subscribe(beep_topic)
    # Make the first telemetry sample due immediately on entering the loop.
    last_publish = ticks_add(ticks_ms(), -500)
    while True:
        # Poll MQTT and call on_message if a command arrives. Transport may still block.
        client.check_msg()
        # Take one timer reading to use for this iteration of the main loop.
        now = ticks_ms()
        # Stop the tone once its deadline is reached, without sleeping for its duration.
        if beep_until is not None and ticks_diff(now, beep_until) >= 0:
            sound.duty_u16(0)
            # Clear the deadline: there is no active tone left to stop.
            beep_until = None
        # Publish every 500 ms while still polling commands between publications.
        if ticks_diff(now, last_publish) >= 500:
            readings = {"left": left.value(), "right": right.value()}
            # Build JSON with the current left/right digital input values.
            payload = json.dumps(readings)
            # Publish to our telemetry topic; subscribers can display the two readings.
            client.publish(line_topic, payload.encode(), retain=False)
            print(payload)
            # Record the sample time so the next publication waits another 500 ms.
            last_publish = now
        # Yield briefly; this is not a 500 ms blocking telemetry delay.
        sleep_ms(10)
finally:
    # Cleanup runs after completion, an error or Ctrl+C.
    # Always switch the LED off when leaving the program.
    led.value(0)
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    # Release the PWM peripheral after normal completion, an error or Ctrl+C.
    sound.deinit()
    # Leave the physical pin LOW after PWM has been released.
    pin.value(0)

    # A failed connection may still have opened a socket that needs closing.
    if client.sock is not None:
        try:
            # Attempt a clean MQTT disconnect before closing the network socket.
            client.disconnect()
        # The network may already be unavailable; still perform local cleanup.
        except OSError:
            pass
        finally:
            # Release the socket even if sending DISCONNECT failed.
            client.sock.close()
