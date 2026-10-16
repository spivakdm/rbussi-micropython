"""Exercise paired routing and watchdogs in an isolated container, without MQTT."""
import json
import math
import os
import subprocess
import sys
import time
import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import String
sys.path.insert(0, '/course')
from paired_drive import wheel_command

assert wheel_command(1.,0.) == (1.,0.,35,35)
assert wheel_command(0.,1.) == (0.,1.,-20,20)
assert max(abs(v) for v in wheel_command(100.,100.)[2:]) <= 40
for value in (math.nan, math.inf):
    try: wheel_command(value,0.)
    except ValueError: pass
    else: raise AssertionError('Nonfinite speed accepted')

rclpy.init()
node=rclpy.create_node('paired_check')
state=node.create_publisher(String,'/robot99/state',1)
command=node.create_publisher(Twist,'/paired/cmd_vel',1)
wheels=[];sim=[]
subs=[node.create_subscription(String,'/robot99/wheels',lambda m:wheels.append(json.loads(m.data)),10),
      node.create_subscription(Twist,'/turtle1/cmd_vel',lambda m:sim.append((m.linear.x,m.angular.z)),10)]
process=subprocess.Popen(['python','/course/paired_drive.py'],env={**os.environ,'ROBOT_NAME':'robot99'})

def cycle(seconds, telemetry=True, motion=None):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if telemetry:state.publish(String(data='{"left_pwm":0,"right_pwm":0,"command_count":1}'))
        if motion is not None:
            m=Twist();m.linear.x,m.angular.z=motion;command.publish(m)
        rclpy.spin_once(node,timeout_sec=.03)
        time.sleep(.02)

def stopped():
    assert len(wheels)>0 and wheels[-1]['left']==0 and wheels[-1]['right']==0,wheels[-5:]
    assert sim[-1]==(0.,0.),sim[-5:]

try:
    cycle(3,False,(.8,0.));stopped()
    cycle(2,True,(.8,0.))
    assert any(m['left']==28 and m['right']==28 and m['duration_ms']==300 for m in wheels)
    assert (.8,0.) in sim
    cycle(1,True,None);stopped()
    cycle(1,True,(0.,1.))
    assert any(m['left']==-20 and m['right']==20 for m in wheels)
    cycle(1,True,(math.nan,0.));stopped()
    cycle(2,False,(.8,0.));stopped()
    cycle(1,True,None);stopped()  # Recovery must not replay an old command.
    competitor=node.create_publisher(Twist,'/turtle1/cmd_vel',1)
    cycle(2,True,(.8,0.));stopped()
    node.destroy_publisher(competitor)
    cycle(1,True,None);stopped()
    print('PASS: routing, clamps, invalid input, input/telemetry watchdogs, conflicting controller, no replay')
finally:
    process.terminate();process.wait(timeout=10)
    node.destroy_node();rclpy.shutdown()
