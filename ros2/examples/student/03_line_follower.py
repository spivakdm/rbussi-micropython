"""Task 3: write the four relay rules. Simulator only."""
import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist


def choose_motion(left, right):
    # TODO: add if/elif/else and return forward speed, turn rate.
    # Straight: 0.9, 0.0. Left: 0.5, 1.8. Right: 0.5, -1.8. Stop: 0.0, 0.0.
    return 0.0, 0.0


rclpy.init()
node = Node('student_line_follower')
publisher = node.create_publisher(Twist, '/turtle1/cmd_vel', 10)
readings = None
received_at = 0


def receive_sensors(message):
    global readings, received_at
    if len(message.data) == 2:
        readings = message.data
        received_at = time.monotonic()


def drive():
    command = Twist()
    if readings is not None and time.monotonic() - received_at < 0.5:
        left, right = readings
        command.linear.x, command.angular.z = choose_motion(left, right)
    publisher.publish(command)


subscription = node.create_subscription(Int32MultiArray, '/sim/line', receive_sensors, 10)
timer = node.create_timer(0.05, drive)
print('Complete choose_motion(). Ctrl+C stops the follower.', flush=True)
try:
    rclpy.spin(node)
except (KeyboardInterrupt, ExternalShutdownException):
    pass
finally:
    if rclpy.ok():
        publisher.publish(Twist())
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
