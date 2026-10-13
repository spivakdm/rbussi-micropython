"""Connect to a 2.4 GHz Wi-Fi network and print the IP in Thonny."""
import network
from time import sleep_ms, ticks_ms, ticks_diff
import network_secrets as settings

wlan = network.WLAN()
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)

started = ticks_ms()
while not wlan.isconnected():
    if ticks_diff(ticks_ms(), started) >= 15000:
        wlan.disconnect()
        raise OSError("Wi-Fi timeout: check 2.4 GHz, password and network access")
    sleep_ms(250)
print("Wi-Fi connected; IP:", wlan.ifconfig()[0])
