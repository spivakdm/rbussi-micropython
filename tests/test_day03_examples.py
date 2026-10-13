"""Host checks for Day 3; simulated hardware and network, no real commands."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples/day03'


class Day03Tests(unittest.TestCase):
    def run_example(self, filename, frames=None, messages=None, stop=700,
                    wifi=True, ntp_fail=False, connect_fail=False,
                    interrupt_sound=False):
        events, clients = [], []
        clock = [0]
        queued = list(messages or [])
        frames = frames or [(0, 0, 0)]
        continuous = filename.startswith(('06_', '07_', '08_', '09_', '10_'))

        def sleep_ms(duration):
            clock[0] += duration
            if interrupt_sound and duration >= 200:
                raise KeyboardInterrupt()
            if continuous and clock[0] >= stop:
                raise KeyboardInterrupt()

        class Pin:
            IN, OUT = 0, 1
            def __init__(self, gpio, mode, value=0):
                self.gpio, self.mode, self.level = gpio, mode, value
            def value(self, value=None):
                if value is not None:
                    self.level = value
                    events.append(('pin', self.gpio, value, clock[0]))
                if self.mode == self.IN:
                    frame = frames[0]
                    for candidate in frames:
                        if candidate[0] <= clock[0]:
                            frame = candidate
                    return frame[1 if self.gpio == 34 else 2]
                return self.level

        class PWM:
            def __init__(self, pin, freq, duty_u16):
                events.append(('pwm_start', freq, duty_u16))
            def freq(self, value):
                events.append(('frequency', value, clock[0]))
            def duty_u16(self, value):
                events.append(('duty', value, clock[0]))
            def deinit(self):
                events.append(('deinit', clock[0]))

        class WLAN:
            def active(self, value): pass
            def isconnected(self): return wifi
            def connect(self, *args): events.append(('wifi_connect',))
            def disconnect(self): events.append(('wifi_disconnect',))
            def ifconfig(self): return ('192.0.2.1', '', '', '')

        class SSLContext:
            def __init__(self, protocol): self.protocol = protocol
            def load_verify_locations(self, cafile):
                events.append(('tls', self.protocol, self.verify_mode, cafile))

        class Socket:
            def close(self): events.append(('socket_close',))

        class MQTT:
            def __init__(self, *args, **kwargs):
                self.sock, self.cb = None, None
                self.args, self.kwargs = args, kwargs
                clients.append(self)
            def connect(self, timeout):
                self.sock = Socket()
                if connect_fail:
                    raise OSError('simulated connection failure')
            def disconnect(self): events.append(('disconnect',))
            def set_callback(self, cb): self.cb = cb
            def subscribe(self, topic): events.append(('subscribe', topic))
            def publish(self, topic, payload, retain):
                events.append(('publish', topic, payload, retain, clock[0]))
            def ping(self): events.append(('ping', clock[0]))
            def check_msg(self):
                while queued and queued[0][0] <= clock[0]:
                    _, suffix, payload = queued.pop(0)
                    self.cb(('edu-test/robot01' + suffix).encode(), payload)

        def settime():
            if ntp_fail:
                raise OSError('simulated NTP failure')
            events.append(('ntp',))

        def module(name, **attrs):
            return types.SimpleNamespace(**attrs)

        modules = {
            'machine': module('machine', Pin=Pin, PWM=PWM),
            'network': module('network', WLAN=WLAN),
            'time': module('time', sleep_ms=sleep_ms, ticks_ms=lambda: clock[0],
                           ticks_diff=lambda a, b: a-b, ticks_add=lambda a, b: a+b,
                           gmtime=lambda: (2026, 10, 13)),
            'ntptime': module('ntptime', settime=settime),
            'ssl': module('ssl', SSLContext=SSLContext,
                          PROTOCOL_TLS_CLIENT='client', CERT_REQUIRED='required'),
            'umqtt': module('umqtt'), 'umqtt.simple': module('simple', MQTTClient=MQTT),
            'network_secrets': module(
                'settings', WIFI_SSID='test', WIFI_PASSWORD='not-real',
                MQTT_HOST='broker.invalid', MQTT_PORT=8883, MQTT_USER='test',
                MQTT_PASSWORD='not-real', ESP32_CLIENT_ID='test-esp32',
                TOPIC_PREFIX='edu-test/robot01', SYNC_NTP=True,
                NTP_HOST='ntp.invalid', CA_FILE='certs/isrg-root-x1.pem'),
        }
        caught = None
        with patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
            try:
                runpy.run_path(str(EXAMPLES / filename))
            except (KeyboardInterrupt, OSError) as error:
                caught = error
        return events, clients, caught

    def assert_sound_closed(self, events):
        self.assertIn('deinit', [e[0] for e in events])
        duties = [e[1] for e in events if e[0] == 'duty']
        self.assertEqual(duties[-1], 0)
        self.assertEqual([e[2] for e in events if e[:2] == ('pin', 26)][-1], 0)

    def test_finite_sound_programs_and_interruption(self):
        for name in ['01_one_sound.py', '02_frequency_and_duty.py', '03_beep_function.py',
                     '11_ode_to_joy.py', '12_twinkle_twinkle.py', '13_robot_sound_signals.py']:
            with self.subTest(name=name):
                events, _, error = self.run_example(name)
                self.assertIsNone(error)
                self.assert_sound_closed(events)
                events, _, error = self.run_example(name, interrupt_sound=True)
                self.assertIsInstance(error, KeyboardInterrupt)
                self.assert_sound_closed(events)

    def test_sound_signal_rests_disable_pwm_without_zero_frequency(self):
        events, _, error = self.run_example('13_robot_sound_signals.py')
        self.assertIsNone(error)
        self.assertNotIn(0, [e[1] for e in events if e[0] == 'frequency'])
        # The success signal's rest starts at 1360 ms and leaves PWM silent.
        self.assertIn(('duty', 0, 1360), events)
        self.assert_sound_closed(events)

    def test_wifi_timeout_does_not_loop_forever(self):
        events, _, error = self.run_example('04_connect_wifi.py', wifi=False)
        self.assertIsInstance(error, OSError)
        self.assertIn('timeout', str(error))
        self.assertIn(('wifi_disconnect',), events)

    def test_hello_verified_tls_no_retention_and_cleanup(self):
        events, clients, error = self.run_example('05_mqtt_hello.py')
        self.assertIsNone(error)
        self.assertIn(('tls', 'client', 'required', 'certs/isrg-root-x1.pem'), events)
        publish = [e for e in events if e[0] == 'publish']
        self.assertEqual(publish[0][1:4], (b'edu-test/robot01/telemetry/hello', b'hello', False))
        self.assertEqual(clients[0].kwargs['keepalive'], 60)
        self.assertIn(('socket_close',), events)

    def test_connection_failure_closes_socket(self):
        events, _, error = self.run_example('05_mqtt_hello.py', connect_fail=True)
        self.assertIsInstance(error, OSError)
        self.assertIn(('socket_close',), events)

    def test_ntp_failure_prevents_mqtt_connection(self):
        _, clients, error = self.run_example('05_mqtt_hello.py', ntp_fail=True)
        self.assertIsInstance(error, OSError)
        self.assertEqual(clients, [])

    def test_periodic_sensor_payloads_follow_inputs(self):
        events, _, _ = self.run_example('06_sensor_telemetry.py',
                                        frames=[(0, 0, 1), (300, 1, 0)], stop=1100)
        payloads = [json.loads(e[2]) for e in events if e[0] == 'publish']
        self.assertEqual(payloads, [{'left': 0, 'right': 1},
                                   {'left': 1, 'right': 0}, {'left': 1, 'right': 0}])

    def test_change_only_and_keepalive_when_idle(self):
        events, _, _ = self.run_example('07_publish_on_change.py',
                                        frames=[(0, 0, 0), (100, 1, 0)], stop=21000)
        payloads = [json.loads(e[2]) for e in events if e[0] == 'publish']
        self.assertEqual(payloads, [{'left': 0, 'right': 0}, {'left': 1, 'right': 0}])
        self.assertTrue(any(e[0] == 'ping' for e in events))
        self.assertIn(('socket_close',), events)

    def test_led_commands_unknown_ignored_and_ctrl_c_off(self):
        events, _, error = self.run_example('08_mqtt_led.py', messages=[
            (0, '/cmd/led', b'ON'), (10, '/cmd/led', b'bad'),
            (20, '/cmd/led', b'OFF'), (30, '/cmd/led', b'ON')])
        self.assertIsInstance(error, KeyboardInterrupt)
        self.assertEqual([e[2] for e in events if e[:2] == ('pin', 2)], [1, 0, 1, 0])

    def test_bad_beep_commands_do_not_stop_program(self):
        invalid = [b'not json', b'[]', b'{}', b'{"frequency":true,"duration_ms":200}',
                   b'{"frequency":2000,"duration_ms":1001}',
                   b'{"frequency":99,"duration_ms":200}',
                   b'{"frequency":2000.5,"duration_ms":200}']
        messages = [(i*10, '/cmd/beep', value) for i, value in enumerate(invalid)]
        messages.append((80, '/cmd/beep', b'{"frequency":2000,"duration_ms":200}'))
        events, _, error = self.run_example('09_mqtt_beep.py', messages=messages)
        self.assertIsInstance(error, KeyboardInterrupt)
        self.assertEqual(len([e for e in events if e[:2] == ('duty', 32768)]), 1)
        self.assert_sound_closed(events)

    def test_combined_sound_does_not_delay_telemetry_or_led(self):
        events, _, error = self.run_example('10_connected_robot.py', stop=1300,
            messages=[(10, '/cmd/beep', b'{"frequency":2000,"duration_ms":1000}'),
                      (20, '/cmd/led', b'ON'), (30, '/cmd/led', b'OFF')])
        self.assertIsInstance(error, KeyboardInterrupt)
        self.assertEqual([e[4] for e in events if e[0] == 'publish'], [0, 500, 1000])
        self.assertIn(('pin', 2, 1, 20), events)
        self.assertIn(('duty', 0, 1010), events)
        self.assert_sound_closed(events)
        self.assertIn(('socket_close',), events)

    def test_computer_command_validation(self):
        namespace = runpy.run_path(str(ROOT / 'tools/mqtt_classroom_client.py'))
        command = namespace['command_message']
        self.assertEqual(command('on'), ('/cmd/led', 'ON'))
        suffix, payload = command('beep 2000 200')
        self.assertEqual(suffix, '/cmd/beep')
        self.assertEqual(json.loads(payload), {'frequency': 2000, 'duration_ms': 200})
        for value in ['motors 100', 'beep 2000 -1', 'beep nope 200', 'beep 9999 20']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                command(value)


if __name__ == '__main__':
    unittest.main()
