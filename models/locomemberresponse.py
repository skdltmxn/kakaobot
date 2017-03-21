# -*- coding: utf-8 -*-

from locoresponse import LocoResponse
from locomember import *


class LocoMemberResponse(LocoResponse):
    def chat_id(self):
        return self._data["chatId"]
        
    def members(self):
        return map(LocoMember, self._data["members"])
