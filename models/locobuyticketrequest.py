# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoBuyTicketRequest(LocoRequest):
    def method(self):
        return "BUY"
