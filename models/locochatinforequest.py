# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoChatInfoRequest(LocoRequest):
    def method(self):
        return "CHATINFO"
