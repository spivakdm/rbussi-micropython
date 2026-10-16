"""Check map RGB at known poses and independence from pen/overlay/resize."""
import time
import ctypes as c
import re
import subprocess
import rclpy
from turtlesim.msg import Color
from turtlesim.srv import TeleportAbsolute, SetPen
from std_msgs.msg import String
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt, QSizeF, QPointF, QRectF

rclpy.init();node=rclpy.create_node('color_check')
latest=None;count=0

def receive(m):
    global latest,count
    latest=(m.r,m.g,m.b);count+=1
sub=node.create_subscription(Color,'/turtle1/color_sensor',receive,10)
teleport=node.create_client(TeleportAbsolute,'/turtle1/teleport_absolute')
pen=node.create_client(SetPen,'/turtle1/set_pen')
overlay=node.create_publisher(String,'/sim/overlay',1)

def wait(predicate):
    deadline=time.monotonic()+10
    while not predicate():
        assert time.monotonic()<deadline,'Timed out'
        rclpy.spin_once(node,timeout_sec=.05)

assert teleport.wait_for_service(timeout_sec=10)
assert pen.wait_for_service(timeout_sec=10)
image=QImage('/course/assets/riihimaki-map.png')
expected=QImage(640,480,QImage.Format_RGB32);expected.fill(Qt.white)
painter=QPainter(expected);painter.setRenderHint(QPainter.SmoothPixmapTransform)
size=QSizeF(image.size()).scaled(QSizeF(640,480),Qt.KeepAspectRatio)
painter.drawImage(QRectF(QPointF((640-size.width())/2,(480-size.height())/2),size),image);painter.end()
colors=set()
try:
    future=pen.call_async(SetPen.Request(r=255,g=0,b=255,width=20,off=0));wait(future.done)
    for px,py in [(100,100),(200,200),(450,200),(500,400)]:
        f=teleport.call_async(TeleportAbsolute.Request(x=px/45.,y=(479-py)/45.,theta=0.));wait(f.done)
        initial=count;wait(lambda:count>initial+4)
        target=expected.pixelColor(px,py);rgb=(target.red(),target.green(),target.blue())
        assert latest==rgb,(px,py,latest,rgb)
        overlay.publish(String(data='{"track":[[0,400],[640,400],[640,410]],"width":20,"sensors":[[500,400,1]]}'))
        initial=count;wait(lambda:count>initial+4)
        assert latest==rgb,('Overlay affected RGB',latest,rgb)
        colors.add(rgb)
    # Resizing the view must not change the sampled logical map coordinate.
    windows=subprocess.check_output(['xwininfo','-root','-tree'],text=True)
    wid=int(re.search(r'(0x[0-9a-f]+) "TurtleSim"',windows).group(1),16)
    x=c.CDLL('libX11.so.6');x.XOpenDisplay.restype=c.c_void_p
    display=c.c_void_p(x.XOpenDisplay(b':0'))
    x.XResizeWindow(display,c.c_ulong(wid),960,540);x.XSync(display,False)
    initial=count;wait(lambda:count>initial+4)
    assert latest==rgb,('Window resize affected RGB',latest,rgb)
    x.XCloseDisplay(display)
    assert len(colors)>1,colors
    print('PASS: RGB matches map pixels at four poses; trails, overlays and resizing do not affect it',colors)
finally:
    node.destroy_node();rclpy.shutdown()
