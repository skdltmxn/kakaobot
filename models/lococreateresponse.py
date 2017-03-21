# -*- coding: utf-8 -*-

from locoresponse import LocoResponse


class LocoCreateResponse(LocoResponse):
    def chat_id(self):
        return self._data["chatId"]
