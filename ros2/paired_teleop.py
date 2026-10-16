"""Hold W/A/S/D to drive both robots; release stops after a short timeout."""
import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import Twist


def main():
    rclpy.init()
    node = rclpy.create_node('paired_keyboard')
    publisher = node.create_publisher(Twist, '/paired/cmd_vel', 1)
    settings = termios.tcgetattr(sys.stdin)
    speed = (0.0, 0.0)
    last_key = 0
    print('PAIRED MODE: W forward, S backward, A left, D right. Space stop. Q quit.')
    print('Hold a key; release stops. Keep focus here. Both robots may move.')
    try:
        tty.setcbreak(sys.stdin.fileno())
        while rclpy.ok():
            if select.select([sys.stdin], [], [], 0.05)[0]:
                key = sys.stdin.read(1).lower()
                if key in ('q', '\x03'):
                    break
                speed = {'w': (0.8, 0.0), 's': (-0.8, 0.0),
                         'a': (0.0, 1.2), 'd': (0.0, -1.2)}.get(key, (0.0, 0.0))
                last_key = time.monotonic()
            msg = Twist()
            if time.monotonic() - last_key < 0.25:
                msg.linear.x, msg.angular.z = speed
            publisher.publish(msg)
            rclpy.spin_once(node, timeout_sec=0)
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        if rclpy.ok():
            publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
