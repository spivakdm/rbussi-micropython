"""Run a complete closed-loop lap, then check the missing-sensor stop."""
import math
import subprocess
import sys
import time
import rclpy
from turtlesim.msg import Pose
from std_msgs.msg import Int32MultiArray
sys.path.insert(0, '/course/simulation')
from line_geometry import TRACK, distance_to_track, pixel

rclpy.init()
node = rclpy.create_node('line_follow_check')
pose = None
readings = None
states = set()

def receive_pose(message):
    global pose
    pose = message

def receive_line(message):
    global readings
    readings = message.data
    states.add(tuple(readings))

sub_pose = node.create_subscription(Pose, '/turtle1/pose', receive_pose, 10)
sub_line = node.create_subscription(Int32MultiArray, '/sim/line', receive_line, 10)
world = subprocess.Popen(['python', '/course/simulation/line_world.py'])
follower = None
try:
    deadline = time.monotonic() + 10
    while readings is None or pose is None:
        assert time.monotonic() < deadline, 'Sensors did not start'
        rclpy.spin_once(node, timeout_sec=0.05)
    assert 'mqtt_bridge' not in node.get_node_names()
    follower = subprocess.Popen(['python', '/course/examples/05_sim_line_follower.py'])
    previous = None
    progress = 0
    max_error = 0
    deadline = time.monotonic() + 100
    while progress < len(TRACK)*2:
        assert time.monotonic() < deadline, 'Robot did not complete two laps'
        assert follower.poll() is None and world.poll() is None, 'Demo process exited'
        rclpy.spin_once(node, timeout_sec=0.05)
        px, py = pixel(pose.x, pose.y)
        error = distance_to_track(px, py)
        max_error = max(max_error, error)
        assert error < 15, 'Robot lost the line'
        index = min(range(len(TRACK)), key=lambda i: math.hypot(TRACK[i][0]-px, TRACK[i][1]-py))
        if previous is not None:
            delta = (index-previous+len(TRACK)//2) % len(TRACK) - len(TRACK)//2
            progress += delta
        previous = index
    assert {(0, 0), (1, 0), (0, 1)} <= states, states
    # Removing the sensor publisher must stop the follower even when it is still running.
    world.terminate()
    world.wait(timeout=5)
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.05)
    assert abs(pose.linear_velocity) < 0.001 and abs(pose.angular_velocity) < 0.001
    print(f'PASS: two laps; both sensors active; maximum centre error {max_error:.1f}px; stale-sensor stop', flush=True)
finally:
    for process in (follower, world):
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
    node.destroy_node()
    rclpy.shutdown()
