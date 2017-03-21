# -*- coding: utf-8 -*-

from gevent import socket
from gevent.pool import Group
from gevent.queue import Queue
from struct import unpack


class TCPClient():
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._group = Group()
        self._send_buffer = Queue()
        self._recv_buffer = Queue()
        
    def connect(self, address):
        self._socket.connect(address)
        self._group.spawn(self._recv_loop)
        self._group.spawn(self._send_loop)
        
    def disconnect(self):
        self._group.kill()
        self._socket.close()
        self._group.join()

    def _recv_loop(self):
        buf = ""
        u4 = lambda x: unpack("<I", x)[0]
        
        while True:
            data = self._socket.recv(8192)
            buf += data

            while len(buf) > 0:
                length = u4(buf[:4])
                if len(buf) - 4 < length:
                    break
    
                self._recv_buffer.put(buf[4:4 + length])
                buf = buf[4 + length:]

    def _send_loop(self):
        while True:
            data = self._send_buffer.get()
            self._socket.sendall(data)

    def write(self, data):
        self._send_buffer.put(data)

    def get_packet(self):
        return self._recv_buffer.get()
