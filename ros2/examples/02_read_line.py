"""A ROS subscriber: read the real robot's two line sensors."""
import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray


def show_line(message):
    left, right = message.data
    print('Left:', left, 'Right:', right)
    if left == 1 and right == 1:
        print('Both sensors see black')


rclpy.init()
node = Node('line_reader', namespace=os.environ['ROBOT_NAME'])
subscription = node.create_subscription(Int32MultiArray, 'line', show_line, 10)
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
