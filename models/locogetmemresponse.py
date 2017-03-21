# -*- coding: utf-8 -*-

from locoresponse import LocoResponse
from locomember import *


class LocoGetMemResponse(LocoResponse):
    def token(self):
        return self._data["token"]
        
    def members(self):
        return map(LocoMember, self._data["members"])
