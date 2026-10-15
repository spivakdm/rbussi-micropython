"""Smoke test inside the desktop container; never connects to MQTT."""
import hashlib
from pathlib import Path
import time
import re
import subprocess
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt
import urllib.request
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import Empty

rclpy.init()
node = Node('simulator_check')
pose = None

def receive(msg):
    global pose
    pose = msg

sub = node.create_subscription(Pose, '/turtle1/pose', receive, 10)
pub = node.create_publisher(Twist, '/turtle1/cmd_vel', 10)
reset = node.create_client(Empty, '/reset')

def wait(test, timeout=15):
    end = time.monotonic() + timeout
    while not test():
        if time.monotonic() > end:
            raise RuntimeError('Simulator check timed out')
        rclpy.spin_once(node, timeout_sec=0.05)

def drive(linear, angular):
    msg = Twist()
    msg.linear.x, msg.angular.z = linear, angular
    end = time.monotonic() + 0.5
    while time.monotonic() < end:
        pub.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.03)
    pub.publish(Twist())
    for _ in range(8):
        rclpy.spin_once(node, timeout_sec=0.03)

try:
    wait(lambda: pose is not None and pub.get_subscription_count() > 0)
    assert 'mqtt_bridge' not in node.get_node_names(), 'MQTT must be opt-in'
    assert reset.wait_for_service(timeout_sec=5)
    future = reset.call_async(Empty.Request())
    wait(future.done)
    wait(lambda: abs(pose.theta) < 0.01 and abs(pose.x - 7.1) < 0.02)
    app = QApplication([])
    windows = subprocess.check_output(['xwininfo', '-root', '-tree'], text=True)
    window = int(re.search(r'(0x[0-9a-f]+) "TurtleSim"', windows).group(1), 16)
    def check_map():
        app.processEvents()
        screenshot = app.primaryScreen().grabWindow(window).toImage()
        assert (screenshot.width(), screenshot.height()) == (640, 480)
        expected_map = QImage('/course/assets/riihimaki-map.png').scaled(
            640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        ox = (640 - expected_map.width()) // 2
        oy = (480 - expected_map.height()) // 2
        for x, y in [(30, 30), (100, 100), (500, 100), (500, 400)]:
            assert screenshot.pixelColor(x+ox, y+oy) == expected_map.pixelColor(x, y), 'Map background missing'
    check_map()
    x = pose.x
    drive(1.0, 0.0)
    assert pose.x - x > 0.2, 'Forward movement failed'
    drive(0.0, 1.0)
    assert pose.theta > 0.2, 'Turn failed'
    future = reset.call_async(Empty.Request())
    wait(future.done)
    wait(lambda: abs(pose.theta) < 0.01 and abs(pose.x - 7.1) < 0.02)
    check_map()
    clear = node.create_client(Empty, '/clear')
    assert clear.wait_for_service(timeout_sec=5)
    future = clear.call_async(Empty.Request())
    wait(future.done)
    time.sleep(0.2)
    check_map()
    expected = Path('/course/assets/rbussi-top.png').read_bytes()
    assert int.from_bytes(expected[16:20], 'big') == 45
    assert int.from_bytes(expected[20:24], 'big') == 45
    for p in Path('/opt/ros/jazzy/share/turtlesim/images').glob('*.png'):
        assert hashlib.sha256(p.read_bytes()).digest() == hashlib.sha256(expected).digest()
    with urllib.request.urlopen('http://127.0.0.1:6080/vnc.html', timeout=5) as page:
        assert page.status == 200
    print('PASS: simulator forward, turn, reset, map pixels after reset/clear, 640x480 field, all RBussi sprites, browser HTTP, MQTT off', flush=True)
finally:
    pub.publish(Twist())
    node.destroy_node()
    rclpy.shutdown()
