"""Packet-level checks: retained commands, fragmented packets and deadlines."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

class Socket:
    def __init__(self, data):
        self.data = data
        self.writes = []
    def read(self, count):
        result, self.data = self.data[:min(count, 2)], self.data[min(count, 2):]
        return result
    def settimeout(self, timeout):
        self.timeout = timeout
    def write(self, data):
        self.writes.append(data)

class TransportTests(unittest.TestCase):
    def client(self, data, clock=lambda:0):
        modules = {'time':types.SimpleNamespace(ticks_ms=clock,ticks_diff=lambda a,b:a-b,ticks_add=lambda a,b:a+b),
                   'umqtt':types.ModuleType('umqtt'),
                   'umqtt.simple':types.SimpleNamespace(MQTTClient=object)}
        with patch.dict(sys.modules, modules):
            spec=importlib.util.spec_from_file_location('robot_mqtt_test',Path(__file__).resolve().parents[1]/'robot/robot_mqtt.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        c=module.RobotMQTT();c.sock=Socket(data);c.received=[]
        c.cb=lambda topic,message:c.received.append((topic,message))
        return c
    def test_live_and_retained(self):
        for flag in [0x30,0x31]:
            c=self.client(bytes([flag,10])+b'\x00\x01tforward')
            c.wait_msg()
            self.assertEqual(c.received,[(b't',b'forward')] if flag==0x30 else [])
    def test_truncated_and_oversized(self):
        for data in [b'\x30\x0a\x00',b'\x30\x81\x08']:
            with self.assertRaises((OSError,ValueError)):
                self.client(data).wait_msg()
    def test_whole_packet_deadline(self):
        tick=iter([0,10,100,201])
        c=self.client(b'\x30\x0a\x00\x01tforward',lambda:next(tick))
        with self.assertRaises(OSError):c.wait_msg()
    def test_qos1_retained_ack_without_dispatch(self):
        c=self.client(b'\x33\x0c\x00\x01t\x00\x07forward')
        c.wait_msg()
        self.assertEqual(c.received,[])
        self.assertEqual(c.sock.writes,[b'\x40\x02\x00\x07'])

if __name__=='__main__':unittest.main()
