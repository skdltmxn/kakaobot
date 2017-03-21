# -*- coding: utf-8 -*-

from locoresponse import LocoResponse
from locochatlog import *


class LocoMessageResponse(LocoResponse):
    def chat_log(self):
        return LocoChatLog(self._data["chatLog"])
        
    def log_id(self):
        return self._data["logId"]
        
    def author(self):
        return self._data["authorNickname"].encode("utf8")
        
    def chat_id(self):
        return self._data["chatId"]
