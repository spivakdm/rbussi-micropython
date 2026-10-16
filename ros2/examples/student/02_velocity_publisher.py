"""Task 2: publish a short movement, then zero velocity. Simulator only."""
import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Twist

rclpy.init()
node = Node('student_velocity_publisher')

# TODO 1: replace None with node.create_publisher(type, topic, 10).
publisher = None
started = time.monotonic()


def send_command():
    command = Twist()
    if time.monotonic() - started < 3.0:
        command.linear.x = 0.0  # TODO 2: choose a slow forward speed, e.g. 0.5.
        command.angular.z = 0.0
    if publisher is not None:
        pass  # TODO 3: publish command here.


timer = node.create_timer(0.05, send_command)
print('Complete the TODOs. Ctrl+C exits this program.', flush=True)
try:
    rclpy.spin(node)
except (KeyboardInterrupt, ExternalShutdownException):
    pass
finally:
    if publisher is not None and rclpy.ok():
        publisher.publish(Twist())
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
