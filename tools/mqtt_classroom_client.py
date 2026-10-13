"""Computer-side MQTT terminal. Run with CPython, not on the ESP32.

Install paho-mqtt==2.1.0; use --config /path/to/network_secrets.py.
One process receives telemetry and sends non-retained LED/sound commands.
"""
import argparse
import json
from pathlib import Path
import runpy
import ssl
import threading


def command_message(text):
    """Return (topic suffix, payload), or reject an unknown command."""
    parts = text.split()
    if parts == ['on']:
        return '/cmd/led', 'ON'
    if parts == ['off']:
        return '/cmd/led', 'OFF'
    if len(parts) == 3 and parts[0] == 'beep':
        frequency, duration_ms = int(parts[1]), int(parts[2])
        if not 100 <= frequency <= 5000 or not 20 <= duration_ms <= 1000:
            raise ValueError('Use 100..5000 Hz and 20..1000 ms')
        return '/cmd/beep', json.dumps(
            {'frequency': frequency, 'duration_ms': duration_ms})
    raise ValueError('Commands: on, off, beep 2000 200, quit')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path,
                        help='Your private network_secrets.py')
    args = parser.parse_args()
    import paho.mqtt.client as mqtt

    settings = runpy.run_path(str(args.config))
    connected = threading.Event()
    accepted = [False]
    prefix = settings['TOPIC_PREFIX']
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=settings['PC_CLIENT_ID'],
                         protocol=mqtt.MQTTv311)
    client.username_pw_set(settings['MQTT_USER'], settings['MQTT_PASSWORD'])
    # Use the supplied CA, relative to the config's directory.
    context = ssl.create_default_context(
        cafile=str(args.config.resolve().parent / settings['CA_FILE']))
    client.tls_set_context(context)

    def on_connect(client, userdata, flags, reason_code, properties):
        accepted[0] = not reason_code.is_failure
        if accepted[0]:
            client.subscribe([(prefix + '/telemetry/#', 0), (prefix + '/status', 0)])
            print('Connected. Waiting for telemetry from', prefix, flush=True)
        else:
            print('MQTT login refused:', reason_code, flush=True)
        connected.set()

    def on_subscribe(client, userdata, mid, reason_codes, properties):
        if any(code.is_failure for code in reason_codes):
            print('Subscription refused: check account permissions', flush=True)
        else:
            print('Subscriptions accepted', flush=True)

    def on_message(client, userdata, message):
        print('\n' + message.topic + ': ' +
              message.payload.decode('utf-8', errors='replace'), flush=True)

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    try:
        client.connect(settings['MQTT_HOST'], settings['MQTT_PORT'], keepalive=60)
        client.loop_start()
        if not connected.wait(15) or not accepted[0]:
            raise RuntimeError('MQTT connection failed; check network and account')
        print('Commands: on, off, beep 2000 200, quit')
        while True:
            text = input('> ').strip()
            if text == 'quit':
                break
            try:
                suffix, payload = command_message(text)
            except ValueError as error:
                print(error)
                continue
            result = client.publish(prefix + suffix, payload, qos=0, retain=False)
            result.wait_for_publish(timeout=5)
            if not result.is_published():
                print('Send timed out; check the connection')
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == '__main__':
    main()
