"""Connect to a 2.4 GHz Wi-Fi network and print the IP in Thonny."""
# network controls the ESP32 Wi-Fi interface.
import network
from time import sleep_ms, ticks_ms, ticks_diff
# Read your private settings file; do not put passwords in this example.
import network_secrets as settings

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


connect_wifi()
