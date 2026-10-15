"""Prepared ROS/MQTT robot application. Upload as main.py for automatic start."""
from machine import Pin, PWM
from time import sleep_ms, ticks_ms, ticks_add, ticks_diff
import json
import network
import network_secrets as settings
from robot import RBussi
from robot_mqtt import RobotMQTT
from drive_command import parse_drive


def run():
    robot = RBussi()
    led = Pin(2, Pin.OUT, value=0)
    piezo_pin = Pin(26, Pin.OUT, value=0)
    sound = PWM(piezo_pin, freq=2000, duty_u16=0)
    left = Pin(34, Pin.IN)
    right = Pin(35, Pin.IN)
    client = None
    move_until = None
    sound_until = None
    speeds = (0, 0)
    last_command = "startup"
    command_count = 0
    ready = False
    prefix = settings.TOPIC_PREFIX

    def on_message(topic, message):
        nonlocal move_until, sound_until, speeds, last_command, command_count
        if not ready:
            return
        suffix = topic.decode().split('/')[-1]
        try:
            if suffix in ('move', 'wheels'):
                a, b, duration = parse_drive(suffix, message)
                robot.motors(a, b)
                speeds = (a, b)
                move_until = ticks_add(ticks_ms(), duration) if (a or b) else None
            elif suffix == 'led':
                if message == b'ON':
                    led.on()
                elif message == b'OFF':
                    led.off()
                else:
                    raise ValueError("LED expects ON or OFF")
            elif suffix == 'beep':
                data = json.loads(message)
                frequency, duration = data['frequency'], data['duration_ms']
                if type(frequency) is not int or type(duration) is not int:
                    raise ValueError("Sound values must be integers")
                if not (100 <= frequency <= 5000 and 20 <= duration <= 1000):
                    raise ValueError("Sound values out of range")
                sound.freq(frequency)
                sound.duty_u16(32768)
                sound_until = ticks_add(ticks_ms(), duration)
            else:
                return
            command_count += 1
            last_command = suffix + ':' + message.decode()
            print('Command:', last_command)
        except (ValueError, KeyError, TypeError):
            robot.stop()
            speeds = (0, 0)
            move_until = None
            print('Invalid command; motors stopped')

    try:
        if prefix.startswith('/') or len(prefix.split('/')) != 2:
            raise ValueError('TOPIC_PREFIX must look like edu-2026-10/robot19')
        wifi = network.WLAN()
        wifi.active(True)
        if not wifi.isconnected():
            wifi.disconnect()
            wifi.active(False)
            sleep_ms(100)
            wifi.active(True)
            wifi.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)
        started = ticks_ms()
        while not wifi.isconnected():
            if ticks_diff(ticks_ms(), started) >= 15000:
                raise OSError('Wi-Fi timeout')
            sleep_ms(100)
        print('Wi-Fi connected')
        client = RobotMQTT(settings.ESP32_CLIENT_ID.encode(), settings.MQTT_HOST,
                           port=settings.MQTT_PORT, user=settings.MQTT_USER.encode(),
                           password=settings.MQTT_PASSWORD.encode(), keepalive=30)
        client.set_callback(on_message)
        client.connect(timeout=3)
        for suffix in ('move', 'wheels', 'led', 'beep'):
            client.subscribe((prefix + '/cmd/' + suffix).encode(), qos=0)
        client.sock.settimeout(0.2)
        ready = True
        print('READY:', prefix)
        last_publish = ticks_add(ticks_ms(), -200)
        while True:
            now = ticks_ms()
            if move_until is not None and ticks_diff(now, move_until) >= 0:
                robot.stop()
                speeds = (0, 0)
                move_until = None
            if sound_until is not None and ticks_diff(now, sound_until) >= 0:
                sound.duty_u16(0)
                sound_until = None
            client.check_msg()
            if ticks_diff(ticks_ms(), last_publish) >= 200:
                readings = {'left': left.value(), 'right': right.value()}
                state = {'left_pwm': speeds[0], 'right_pwm': speeds[1],
                         'led': led.value(), 'command_count': command_count,
                         'last_command': last_command}
                for name, data in (('line', readings), ('state', state)):
                    client.publish((prefix + '/telemetry/' + name).encode(),
                                   json.dumps(data).encode(), retain=False)
                last_publish = ticks_ms()
            sleep_ms(10)
    finally:
        robot.close()
        led.off()
        sound.duty_u16(0)
        sound.deinit()
        piezo_pin.value(0)
        if client is not None and client.sock is not None:
            client.sock.close()
        print('Robot stopped. Restart after correcting any connection error.')


run()
