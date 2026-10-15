"""One ROS 2 node connecting the student's ROS topics to their MQTT account."""
import json
import os
import re

import paho.mqtt.client as mqtt
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray, String


class RobotBridge(Node):
    def __init__(self):
        name = os.environ['ROBOT_NAME']
        if not re.fullmatch(r'robot[0-9]{2}', name):
            raise ValueError('ROBOT_NAME must look like robot01')
        super().__init__('mqtt_bridge', namespace=name)
        self.prefix = os.environ['MQTT_PREFIX']
        if self.prefix.startswith('/') or self.prefix.split('/')[-1] != name:
            raise ValueError('MQTT_PREFIX must end with your ROBOT_NAME, without a leading /')
        self.connected = False
        self.line = self.create_publisher(Int32MultiArray, 'line', 10)
        self.state = self.create_publisher(String, 'state', 10)
        self.commands = []
        for suffix in ('move', 'wheels', 'led', 'beep'):
            self.commands.append(self.create_subscription(
                String, suffix, lambda msg, key=suffix: self.send(key, msg.data), 10))
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id=os.environ['MQTT_CLIENT_ID'],
                                  clean_session=True, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASSWORD'])
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.connect(os.environ['MQTT_HOST'], int(os.environ.get('MQTT_PORT', '1883')), 30)
        # One ROS thread handles ROS callbacks and MQTT polling.
        self.create_timer(0.02, self.poll)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.connected = not reason_code.is_failure
        if self.connected:
            client.subscribe(self.prefix + '/telemetry/#', qos=0)
            self.get_logger().info('MQTT connected: ' + self.prefix)
        else:
            self.get_logger().error('MQTT login rejected: ' + str(reason_code))

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected = False
        self.get_logger().warning('MQTT disconnected; restart the bridge after fixing the connection')

    def poll(self):
        result = self.client.loop(timeout=0.0)
        if result != mqtt.MQTT_ERR_SUCCESS:
            self.connected = False

    def send(self, suffix, payload):
        if not self.connected:
            self.get_logger().warning('Command dropped: MQTT is offline')
            return
        if len(payload.encode()) > 256:
            self.get_logger().warning('Command dropped: payload too long')
            return
        result = self.client.publish(self.prefix + '/cmd/' + suffix,
                                     payload, qos=0, retain=False)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            self.get_logger().warning('Command was not sent')

    def on_message(self, client, userdata, message):
        if message.retain:
            return
        try:
            payload = message.payload.decode()
            data = json.loads(payload)
            if message.topic == self.prefix + '/telemetry/line':
                values = [data['left'], data['right']]
                if any(type(v) is not int or v not in (0, 1) for v in values):
                    return
                msg = Int32MultiArray()
                msg.data = values
                self.line.publish(msg)
            elif message.topic == self.prefix + '/telemetry/state':
                msg = String()
                msg.data = payload
                self.state.publish(msg)
        except (ValueError, KeyError, TypeError):
            self.get_logger().warning('Ignored invalid telemetry')

    def close(self):
        if self.connected:
            self.client.publish(self.prefix + '/cmd/move', 'stop', qos=0, retain=False)
        self.client.disconnect()
        self.destroy_node()


def main():
    rclpy.init()
    node = None
    try:
        node = RobotBridge()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.close()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
