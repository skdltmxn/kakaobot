# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoLoginListRequest(LocoRequest):
    def method(self):
        return "LOGINLIST"
