# -*- coding: utf-8 -*-

from locoresponse import LocoResponse


class LocoBuyTicketResponse(LocoResponse):
    def host(self):
        return self._data["host"]
    
    def port(self):
        return self._data["port"]
