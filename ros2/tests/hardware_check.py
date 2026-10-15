"""Run inside the container. --move also requests two short wheel tests."""
import argparse
import json
import os
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray, String

parser = argparse.ArgumentParser()
parser.add_argument('--move', action='store_true')
args = parser.parse_args()
rclpy.init()
node = Node('hardware_check', namespace=os.environ['ROBOT_NAME'])
state = {}
line = []

def state_received(message):
    state.clear()
    state.update(json.loads(message.data))

def line_received(message):
    line[:] = message.data

sub_state = node.create_subscription(String, 'state', state_received, 10)
sub_line = node.create_subscription(Int32MultiArray, 'line', line_received, 10)
publishers = {name: node.create_publisher(String, name, 10) for name in ('led', 'move', 'wheels')}

def wait(predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() >= deadline:
            raise RuntimeError('Expected robot response did not arrive')
        rclpy.spin_once(node, timeout_sec=0.05)

def send(name, text):
    message = String()
    message.data = text
    publishers[name].publish(message)

try:
    wait(lambda: len(line) == 2 and bool(state) and all(p.get_subscription_count() for p in publishers.values()))
    print('PASS: ESP32 → MQTT → ROS line readings:', line, flush=True)
    before = state['command_count']
    send('led', 'ON')
    wait(lambda: state.get('led') == 1 and state['command_count'] > before)
    send('led', 'OFF')
    wait(lambda: state.get('led') == 0)
    print('PASS: ROS → MQTT → ESP32 LED ON/OFF confirmed by state telemetry', flush=True)
    if args.move:
        send('move', 'forward')
        wait(lambda: state.get('left_pwm') == 40 and state.get('right_pwm') == 40)
        started = time.monotonic()
        wait(lambda: state.get('left_pwm') == 0 and state.get('right_pwm') == 0, 3)
        print('PASS: forward → automatic stop; observed interval:', round(time.monotonic()-started, 2), flush=True)
        send('wheels', '{"left":30,"right":30,"duration_ms":1000}')
        wait(lambda: state.get('left_pwm') == 30)
        started = time.monotonic()
        send('move', 'stop')
        wait(lambda: state.get('left_pwm') == 0 and state.get('right_pwm') == 0, 3)
        elapsed = time.monotonic() - started
        if elapsed >= 0.8:
            raise RuntimeError('Stop response too slow to distinguish from automatic timeout')
        print('PASS: explicit stop during motion; observed response:', round(elapsed, 2), flush=True)
finally:
    send('move', 'stop')
    send('led', 'OFF')
    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)
    node.destroy_node()
    rclpy.shutdown()
