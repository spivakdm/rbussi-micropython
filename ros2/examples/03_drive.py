"""Send one forward request after the bridge subscribes. Wheels lifted first."""
import os
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

rclpy.init()
node = Node('drive_once', namespace=os.environ['ROBOT_NAME'])
publisher = node.create_publisher(String, 'move', 10)
try:
    deadline = time.monotonic() + 5
    while publisher.get_subscription_count() == 0:
        if time.monotonic() >= deadline:
            raise RuntimeError('No bridge subscriber found')
        rclpy.spin_once(node, timeout_sec=0.1)
    message = String()
    message.data = 'forward'
    publisher.publish(message)
    print('Sent forward; the robot stops after one second')
    rclpy.spin_once(node, timeout_sec=0.2)
finally:
    node.destroy_node()
    rclpy.shutdown()
