"""Test motor timeout, stop and error cleanup without physical hardware."""
import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "robot"))

class AppTests(unittest.TestCase):
    def run_app(self, frames, fail=False):
        clock = [0]
        events = []
        queued = list(frames)
        class Robot:
            def __init__(self): pass
            def motors(self,a,b): events.append(('motors',a,b,clock[0]))
            def stop(self): events.append(('stop',clock[0]))
            def close(self): events.append(('close',clock[0]))
        class Pin:
            OUT=1; IN=0
            def __init__(self,*a,value=0):self.v=value
            def value(self, value=None):
                if value is not None:self.v=value
                return self.v
            def on(self):self.v=1
            def off(self):self.v=0
        class PWM:
            def __init__(self,*a,**kw):pass
            def duty_u16(self,v):pass
            def freq(self,v):pass
            def deinit(self):pass
        class Socket:
            def settimeout(self,v):pass
            def close(self):events.append(('socket_close',))
        class MQTT:
            def __init__(self,*a,**kw):self.sock=Socket()
            def set_callback(self,cb):self.cb=cb
            def connect(self,timeout):pass
            def subscribe(self,*a,**kw):pass
            def publish(self,*a,**kw):pass
            def check_msg(self):
                if fail and clock[0]>=100:raise OSError('network failed')
                while queued and queued[0][0]<=clock[0]:
                    _,suffix,data=queued.pop(0)
                    self.cb(('edu-test/robot01/cmd/'+suffix).encode(),data)
                if clock[0]>=1200:raise KeyboardInterrupt()
        wlan=types.SimpleNamespace(active=lambda v:None,isconnected=lambda:True)
        def sleep(ms):clock[0]+=ms
        m={'robot':types.SimpleNamespace(RBussi=Robot),'machine':types.SimpleNamespace(Pin=Pin,PWM=PWM),
           'robot_mqtt':types.SimpleNamespace(RobotMQTT=MQTT),'network':types.SimpleNamespace(WLAN=lambda:wlan),
           'network_secrets':types.SimpleNamespace(TOPIC_PREFIX='edu-test/robot01',ESP32_CLIENT_ID='test',MQTT_HOST='invalid',MQTT_PORT=1883,MQTT_USER='test',MQTT_PASSWORD='test'),
           'time':types.SimpleNamespace(ticks_ms=lambda:clock[0],ticks_add=lambda a,b:a+b,ticks_diff=lambda a,b:a-b,sleep_ms=sleep)}
        with patch.dict(sys.modules,m):
            try:runpy.run_path(str(ROOT/'robot/main.py'))
            except (KeyboardInterrupt,OSError):pass
        return events
    def test_no_commands_no_motion(self):
        events=self.run_app([])
        self.assertFalse(any(e[0]=='motors' for e in events))
        self.assertIn(('close',1200),events)
    def test_timeout_and_explicit_stop(self):
        events=self.run_app([(0,'move',b'forward')])
        self.assertIn(('motors',40,40,0),events)
        self.assertIn(('stop',1000),events)
        events=self.run_app([(0,'move',b'forward'),(100,'move',b'stop')])
        self.assertIn(('motors',0,0,100),events)
    def test_invalid_command_and_network_failure_stop(self):
        events=self.run_app([(0,'move',b'forward'),(100,'move',b'invalid')])
        self.assertIn(('stop',100),events)
        events=self.run_app([(0,'move',b'forward')],fail=True)
        self.assertIn(('close',100),events)
        self.assertIn(('socket_close',),events)

if __name__=='__main__':unittest.main()
