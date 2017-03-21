# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoPingRequest(LocoRequest):
    def method(self):
        return "PING"
