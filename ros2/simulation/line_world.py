"""Virtual digital sensors and the visible track. No MQTT or hardware access."""
import json
import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Int32MultiArray, String
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute, SetPen
from std_srvs.srv import Empty
from line_geometry import TRACK, LINE_WIDTH, sensors, start_pose


class LineWorld(Node):
    def __init__(self):
        super().__init__('sim_line_sensors')
        self.pose = None
        self.received_at = 0
        self.line = self.create_publisher(Int32MultiArray, '/sim/line', 10)
        self.overlay = self.create_publisher(String, '/sim/overlay', 1)
        self.stop = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(Pose, '/turtle1/pose', self.receive, 10)

    def receive(self, pose):
        self.pose = pose
        self.received_at = time.monotonic()

    def call(self, kind, name, request):
        client = self.create_client(kind, name)
        if not client.wait_for_service(timeout_sec=5):
            raise RuntimeError('Simulator service is unavailable: ' + name)
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5)
        if not future.done() or future.exception():
            raise RuntimeError('Simulator service failed: ' + name)
        self.destroy_client(client)

    def prepare(self):
        # Start every exercise at the same point; drawing trails must not hide the line.
        self.stop.publish(Twist())
        self.call(SetPen, '/turtle1/set_pen', SetPen.Request(off=1))
        x, y, theta = start_pose()
        self.call(TeleportAbsolute, '/turtle1/teleport_absolute',
                  TeleportAbsolute.Request(x=x, y=y, theta=theta))
        self.call(Empty, '/clear', Empty.Request())
        self.timer = self.create_timer(0.05, self.sample)
        self.get_logger().info('Track ready. /sim/line: left, right; white=0, black=1')

    def sample(self):
        if self.pose is None or time.monotonic() - self.received_at > 0.5:
            return
        values = sensors(self.pose.x, self.pose.y, self.pose.theta)
        self.line.publish(Int32MultiArray(data=[s[2] for s in values]))
        self.overlay.publish(String(data=json.dumps({
            'track': TRACK, 'width': LINE_WIDTH, 'sensors': values})))


def main():
    rclpy.init()
    node = LineWorld()
    try:
        node.prepare()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.stop.publish(Twist())
            node.overlay.publish(String(data='{}'))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
