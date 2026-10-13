"""Publish one hello message. Start the computer subscriber first."""

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


# Prepare Wi-Fi, UTC time, verified TLS and our assigned MQTT identity.
client = make_client()
try:
    # Connect to the broker and authenticate; initial socket timeout is 10 s.
    client.connect(timeout=10)
    # Build a concrete topic in our own namespace; .encode() makes bytes.
    topic = (settings.TOPIC_PREFIX + "/telemetry/hello").encode()
    # Send bytes; b"hello" is already bytes. Do not store a retained copy.
    client.publish(topic, b"hello", retain=False)
    print("Sent hello to", topic)
finally:
    # Cleanup runs after completion, an error or Ctrl+C.
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
