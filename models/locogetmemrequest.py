# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoGetMemRequest(LocoRequest):
    def method(self):
        return "GETMEM"
