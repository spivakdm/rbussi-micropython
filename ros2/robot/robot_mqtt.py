"""Bounded MQTT reads and retained-command filtering for the prepared robot app.

Uses the supplied upstream umqtt client for connect/publish/subscribe. Unlike
its default wait_msg(), packet reads share a 200 ms deadline and commands
marked retained are discarded before the application callback.
"""
from time import ticks_ms, ticks_diff, ticks_add
from umqtt.simple import MQTTClient


class RobotMQTT(MQTTClient):
    def _read_exact(self, count, deadline):
        result = bytearray()
        while len(result) < count:
            remaining = ticks_diff(deadline, ticks_ms())
            if remaining <= 0:
                raise OSError("MQTT packet timeout")
            self.sock.settimeout(remaining / 1000)
            chunk = self.sock.read(count - len(result))
            if not chunk:
                raise OSError("MQTT disconnected or incomplete packet")
            result.extend(chunk)
        return bytes(result)

    def wait_msg(self):
        first = self.sock.read(1)
        self.sock.settimeout(0.2)
        if first is None:
            return None
        if not first:
            raise OSError("MQTT disconnected")
        op = first[0]
        deadline = ticks_add(ticks_ms(), 200)
        if op == 0xD0:
            if self._read_exact(1, deadline) != b"\x00":
                raise ValueError("Bad ping response")
            return None
        if op & 0xF0 != 0x30:
            # The upstream subscribe() reads the SUBACK body itself.
            return op
        size = 0
        for shift in range(0, 28, 7):
            digit = self._read_exact(1, deadline)[0]
            size |= (digit & 127) << shift
            if not digit & 128:
                break
        else:
            raise ValueError("Bad MQTT length")
        if size > 1024 or size < 2:
            raise ValueError("MQTT packet too large or short")
        packet = self._read_exact(size, deadline)
        length = packet[0] * 256 + packet[1]
        end = 2 + length
        qos = (op >> 1) & 3
        if length == 0 or end > size or qos > 1:
            raise ValueError("Unsupported MQTT packet")
        topic = packet[2:end]
        if qos:
            if end + 2 > size:
                raise ValueError("Missing packet ID")
            packet_id = packet[end:end + 2]
            end += 2
        if not (op & 1):
            self.cb(topic, packet[end:])
        if qos == 1:
            self.sock.write(b"\x40\x02" + packet_id)
        return op
