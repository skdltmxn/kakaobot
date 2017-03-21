# -*- coding: utf-8 -*-

import bson
from struct import pack, unpack


class LocoPacketError(Exception):
    DATA_TOO_SHORT = 1

    def __init__(self, why):
        Exception.__init__(self)
        self._why = why

    def why(self):
        return self._why


class LocoPacketHeader(object):
    def __init__(self, packet_id, status, method):
        self._packet_id = packet_id
        self._status = status
        self._method = method
        self._body_length = 0

    def set_body_length(self, length):
        self._body_length = length

    def bytes(self):
        ret = pack("<I", self._packet_id)
        ret += pack("<H", self._status)
        ret += self._method.ljust(11, "\x00")
        ret += chr(0)
        ret += pack("<I", self._body_length)
        return ret

    def packet_id(self):
        return self._packet_id

    def status(self):
        return self._status

    def method(self):
        return self._method

    def body_length(self):
        return self._body_length


class LocoPacket(object):
    def __init__(self, packet_id, status, method, data):
        self._packet_header = LocoPacketHeader(packet_id, status, method)
        self._packet_body = bson.dumps(data)
        self._packet_header.set_body_length(len(self._packet_body))

    def bytes(self):
        return self._packet_header.bytes() + self._packet_body

    def body(self):
        return bson.loads(self._packet_body)

    def header(self):
        return self._packet_header
        
    def __len__(self):
        return len(self._packet_body) + 22

    @staticmethod
    def from_raw_bytes(data):
        packet_id = unpack("<I", data[:4])[0]
        status = unpack("<H", data[4:6])[0]
        method = data[6:17].strip("\x00")
        body_length = unpack("<I", data[18:22])[0]

        if body_length != len(data) - 22:
            raise LocoPacketError(LocoPacketError.DATA_TOO_SHORT)

        packet = LocoPacket(packet_id, status, method, bson.loads(data[22:]))
        assert body_length == packet.header().body_length()
        return packet
