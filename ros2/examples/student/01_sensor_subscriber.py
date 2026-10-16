"""Task 1: subscribe to /sim/line and print both sensors."""
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Int32MultiArray

rclpy.init()
node = Node('student_sensor_reader')


def show_sensors(message):
    left, right = message.data
    print('Left:', left, 'Right:', right, flush=True)


# TODO 1: replace None with node.create_subscription(type, topic, callback, 10).
subscription = None

if subscription is None:
    print('Complete TODO 1, save the file, then restart it.', flush=True)

try:
    rclpy.spin(node)
except (KeyboardInterrupt, ExternalShutdownException):
    pass
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
