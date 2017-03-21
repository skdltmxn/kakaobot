# -*- coding: utf-8 -*-

from locoresponse import LocoResponse
from locochatlog import *


class LocoMChatLogsResponse(LocoResponse):
    def chat_logs(self):
        return map(LocoChatLog, self._data["chatLogs"])
        
    def eof(self):
        return self._data["eof"]
