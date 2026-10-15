"""A ROS publisher: alternate ON and OFF once per second. Ctrl+C stops."""
import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Blink(Node):
    def __init__(self):
        super().__init__('blink', namespace=os.environ['ROBOT_NAME'])
        self.publisher = self.create_publisher(String, 'led', 10)
        self.is_on = False
        self.create_timer(1.0, self.blink)

    def blink(self):
        self.is_on = not self.is_on
        message = String()
        message.data = 'ON' if self.is_on else 'OFF'
        self.publisher.publish(message)
        self.get_logger().info(message.data)


rclpy.init()
node = Blink()
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
