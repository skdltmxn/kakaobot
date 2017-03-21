# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoCreateRequest(LocoRequest):
    def method(self):
        return "CREATE"
