# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoMChatLogsRequest(LocoRequest):
    def method(self):
        return "MCHATLOGS"
