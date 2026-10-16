"""Display the virtual sensors: white = 0, black = 1."""
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Int32MultiArray

rclpy.init()
node = Node('sim_line_reader')


def show(message):
    left, right = message.data
    print('Left:', left, 'Right:', right, flush=True)


subscription = node.create_subscription(Int32MultiArray, '/sim/line', show, 10)
try:
    rclpy.spin(node)
except (KeyboardInterrupt, ExternalShutdownException):
    pass
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
