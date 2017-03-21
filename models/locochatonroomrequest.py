# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoChatOnRoomRequest(LocoRequest):
    def method(self):
        return "CHATONROOM"
