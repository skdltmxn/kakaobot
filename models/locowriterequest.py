# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoWriteRequest(LocoRequest):
    def method(self):
        return "WRITE"
