"""Two digital sensors and a relay controller. Simulator only."""
import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist


def steering(left, right):
    if left == 0 and right == 0:
        return 0.9, 0.0        # Line between the sensors: straight.
    elif left == 1 and right == 0:
        return 0.5, 1.8        # Line on the left: turn left.
    elif left == 0 and right == 1:
        return 0.5, -1.8       # Line on the right: turn right.
    else:
        return 0.0, 0.0       # Both black: stop.


def main():
    rclpy.init()
    node = Node('sim_line_follower')
    publisher = node.create_publisher(Twist, '/turtle1/cmd_vel', 10)
    readings = None
    received_at = 0

    def receive(message):
        nonlocal readings, received_at
        if len(message.data) == 2:
            readings = message.data
            received_at = time.monotonic()

    def drive():
        command = Twist()
        if readings is not None and time.monotonic() - received_at < 0.5:
            command.linear.x, command.angular.z = steering(*readings)
        publisher.publish(command)

    subscription = node.create_subscription(Int32MultiArray, '/sim/line', receive, 10)
    timer = node.create_timer(0.05, drive)
    print('Following /sim/line. Ctrl+C stops the simulated robot.', flush=True)
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


if __name__ == '__main__':
    main()
