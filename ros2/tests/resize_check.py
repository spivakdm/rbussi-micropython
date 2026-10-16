"""Check the resizable simulator view inside an isolated desktop container."""
import ctypes as c
import re
import subprocess
import time
from PyQt5.QtWidgets import QApplication
import rclpy
from turtlesim.msg import Pose

app = QApplication([])
rclpy.init()
node = rclpy.create_node('resize_check')
pose = None

def receive(message):
    global pose
    pose = message

subscription = node.create_subscription(Pose, '/turtle1/pose', receive, 10)

def settle():
    for _ in range(12):
        app.processEvents()
        rclpy.spin_once(node, timeout_sec=0.05)
        time.sleep(0.02)

windows = subprocess.check_output(['xwininfo', '-root', '-tree'], text=True)
wid = int(re.search(r'(0x[0-9a-f]+) "TurtleSim"', windows).group(1), 16)
x = c.CDLL('libX11.so.6')
t = c.CDLL('libXtst.so.6')
x.XOpenDisplay.restype = c.c_void_p
display = c.c_void_p(x.XOpenDisplay(b':0'))

def geometry():
    info = subprocess.check_output(['xwininfo', '-id', hex(wid)], text=True)
    return [int(re.search(label + r':\s+(-?\d+)', info)[1])
            for label in ['Absolute upper-left X', 'Absolute upper-left Y', 'Width', 'Height']]

def button(offset):
    root, parent = c.c_ulong(), c.c_ulong()
    children = c.POINTER(c.c_ulong)()
    count = c.c_uint()
    x.XQueryTree(display, c.c_ulong(wid), c.byref(root), c.byref(parent),
                 c.byref(children), c.byref(count))
    x.XRaiseWindow(display, parent)
    if children:
        x.XFree(children)
    x.XSync(display, False)
    time.sleep(0.1)
    a, b, width, height = geometry()
    t.XTestFakeMotionEvent(display, -1, a + width - offset, b - 10, 0)
    t.XTestFakeButtonEvent(display, 1, 1, 0)
    x.XSync(display, False)
    time.sleep(0.1)
    t.XTestFakeButtonEvent(display, 1, 0, 0)
    x.XSync(display, False)
    settle()

try:
    settle()
    assert pose is not None
    original = (pose.x, pose.y, pose.theta)
    assert 'mqtt_bridge' not in node.get_node_names()
    # Resize to a wide view: the 4:3 scene must remain centered with side margins.
    x.XResizeWindow(display, c.c_ulong(wid), 960, 540)
    x.XSync(display, False)
    settle()
    assert geometry()[2:] == [960, 540]
    assert (pose.x, pose.y, pose.theta) == original, 'Resize changed ROS pose'
    screenshot = app.primaryScreen().grabWindow(wid).toImage()
    # A plain background margin and the lavender top-left corner of the map.
    assert screenshot.pixelColor(10, 10).getRgb()[:3] == (245, 247, 250)
    colour = screenshot.pixelColor(125, 5)
    assert colour.blue() > colour.red() and colour.blue() > 200, 'Map did not scale/center'
    button(25)  # Maximize using the actual title-bar control.
    assert 'MAXIMIZED_HORZ' in subprocess.check_output(
        ['xprop', '-id', hex(wid), '_NET_WM_STATE'], text=True)
    assert geometry()[2] > 960
    assert (pose.x, pose.y, pose.theta) == original
    button(25)  # Restore.
    assert geometry()[2:] == [960, 540]
    button(41)  # Minimize, then restore the existing window.
    assert 'HIDDEN' in subprocess.check_output(
        ['xprop', '-id', hex(wid), '_NET_WM_STATE'], text=True)
    x.XMapWindow(display, c.c_ulong(wid))
    x.XResizeWindow(display, c.c_ulong(wid), 640, 480)
    x.XSync(display, False)
    settle()
    assert geometry()[2:] == [640, 480]
    assert (pose.x, pose.y, pose.theta) == original
    print('PASS: resize, proportional map, maximize/restore, minimize/restore, unchanged ROS pose')
finally:
    x.XCloseDisplay(display)
    node.destroy_node()
    rclpy.shutdown()
