# -*- coding: utf-8 -*-

from crypto import cryptor
from models.locopacket import *
from struct import unpack, pack
from util import tcpclient
import gevent
from gevent.event import AsyncResult


class LocoAgent(object):
    def __init__(self):
        self._tcp = tcpclient.TCPClient()
        self._packet_processor = gevent.spawn(self._process_packet)
        self._current_packet_id = 100000000
        self._cryptor = cryptor.Cryptor()
        self._packet_id_request = {}
        self._packet_handler = {}
        self._packet_handler_method = {}
        self._pending_packet = ""

    def _process_packet(self):
        tcp = self._tcp
        buf = ""

        while True:
            buf += self._cryptor.decrypt_aes(tcp.get_packet())

            try:
                packet = LocoPacket.from_raw_bytes(buf)
                packet_id = packet.header().packet_id()
                buf = buf[len(packet):]

                if packet_id in self._packet_handler:
                    self._packet_handler[packet_id].set(packet.body())
                else:
                    method = packet.header().method()
                    if method in self._packet_handler_method:
                        gevent.spawn(self._packet_handler_method[method], packet.body())
                    else:
                        print "{0} | {1}".format(packet.header().method(), packet.body())
            except LocoPacketError as e:
                if e.why() == LocoPacketError.DATA_TOO_SHORT:
                    continue

    def _next_packet_id(self):
        if self._current_packet_id == 200000000:
            self._current_packet_id = 100000000

        packet_id = self._current_packet_id
        self._current_packet_id += 1
        return packet_id

    def _handshake(self):
        key_iv = self._cryptor.get_aes_key_iv()
        encrypted = self._cryptor.encrypt_rsa(key_iv)
        packet = pack("<I", len(encrypted))
        packet += pack("<I", 8)
        packet += pack("<I", 2)
        packet += encrypted
        self._tcp.write(packet)

    def connect(self, host, port):
        self._tcp.connect((host, port))
        self._handshake()
            
    def close(self):
        self._tcp.disconnect()
        self._packet_processor.kill()
        
    def join(self):
        self._packet_processor.join()

    def send_request(self, request):
        packet_id = self._next_packet_id()
        packet = LocoPacket(packet_id, 0, request.method(), request.data())
        encrypted = self._cryptor.encrypt_aes(packet.bytes())
        encrypted = pack("<I", len(encrypted)) + encrypted
        
        self._packet_handler[packet_id] = AsyncResult()
        self._tcp.write(encrypted)
        result = self._packet_handler[packet_id].get()
        del self._packet_handler[packet_id]
        return result

    def set_packet_handler_method(self, method, handler):
        self._packet_handler_method[method] = handler
