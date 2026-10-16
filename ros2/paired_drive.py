"""Opt-in command mirroring, not measured pose synchronization."""
import json
import math
import os
import re
import signal
import time

import rclpy
from rclpy.signals import SignalHandlerOptions
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray, String

INPUT_TIMEOUT = 0.4
TELEMETRY_TIMEOUT = 1.0
LEASE_MS = 300
MAX_PWM = 40


def wheel_command(forward, turn):
    """Map simulator velocity to approximate PWM; there are no wheel encoders."""
    if not math.isfinite(forward) or not math.isfinite(turn):
        raise ValueError('Speeds must be finite')
    forward = max(-1.0, min(1.0, forward))
    turn = max(-1.5, min(1.5, turn))
    left, right = 35 * forward - 20 * turn, 35 * forward + 20 * turn
    scale = max(1.0, abs(left) / MAX_PWM, abs(right) / MAX_PWM)
    return forward, turn, round(left / scale), round(right / scale)


class PairedDrive(Node):
    def __init__(self):
        super().__init__('paired_drive')
        self.robot = os.environ.get('ROBOT_NAME', 'robot01')
        if not re.fullmatch(r'robot[0-9]{2}', self.robot):
            raise ValueError('ROBOT_NAME must look like robot01')
        self.sim = self.create_publisher(Twist, '/turtle1/cmd_vel', 1)
        self.wheels = self.create_publisher(String, '/' + self.robot + '/wheels', 1)
        self.panel = self.create_publisher(String, '/sim/real_sensors', 1)
        self.command = (0.0, 0.0, 0, 0)
        self.command_at = 0
        self.state_at = 0
        self.line_at = 0
        self.line = [0, 0]
        self.enabled = False
        self.create_subscription(Twist, '/paired/cmd_vel', self.receive_command, 1)
        self.create_subscription(String, '/' + self.robot + '/state', self.receive_state, 1)
        self.create_subscription(Int32MultiArray, '/' + self.robot + '/line', self.receive_line, 1)
        self.create_timer(0.1, self.tick)
        self.get_logger().info('Paired mode: /paired/cmd_vel -> simulator + ' + self.robot)
        self.get_logger().info('Stop sim-line-track, sim-line-demo and other controllers. Waiting for fresh robot telemetry.')

    def receive_state(self, message):
        try:
            data = json.loads(message.data)
            if all(type(data[k]) is int for k in ('left_pwm', 'right_pwm', 'command_count')):
                self.state_at = time.monotonic()
        except (ValueError, KeyError, TypeError):
            pass

    def receive_line(self, message):
        if len(message.data) == 2 and all(v in (0, 1) for v in message.data):
            self.line = list(message.data)
            self.line_at = time.monotonic()

    def receive_command(self, message):
        # A new input is required after telemetry recovers; do not replay an old command.
        if not self.enabled:
            return
        try:
            self.command = wheel_command(message.linear.x, message.angular.z)
            self.command_at = time.monotonic()
        except ValueError:
            self.command_at = 0

    def send(self, command):
        forward, turn, left, right = command
        msg = Twist()
        msg.linear.x, msg.angular.z = forward, turn
        self.sim.publish(msg)
        self.wheels.publish(String(data=json.dumps({
            'left': left, 'right': right, 'duration_ms': LEASE_MS})))

    def tick(self):
        now = time.monotonic()
        ready = now - self.state_at < TELEMETRY_TIMEOUT
        # Competing simulator controllers must be stopped before paired driving.
        ready = ready and self.count_publishers('/turtle1/cmd_vel') == 1
        if ready != self.enabled:
            self.get_logger().info('Ready for new commands' if ready else 'Stopped: telemetry missing or another simulator controller is active')
        self.enabled = ready
        if not ready:
            self.command_at = 0
        active = ready and now - self.command_at < INPUT_TIMEOUT
        self.send(self.command if active else (0.0, 0.0, 0, 0))
        self.panel.publish(String(data=json.dumps({
            'robot': self.robot, 'left': self.line[0], 'right': self.line[1],
            'fresh': now - self.line_at < TELEMETRY_TIMEOUT})))


def main():
    def stop(signum, frame):
        raise KeyboardInterrupt

    # Keep ROS alive until finally sends the explicit stop message.
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    node = PairedDrive()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.send((0.0, 0.0, 0, 0))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
