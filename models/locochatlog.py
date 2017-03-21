# -*- coding: utf-8 -*-


class LocoChatLog(object):
    def __init__(self, data):
        self._data = data
    
    def msg_id(self):
        return self._data["msgId"]
        
    def send_at(self):
        return self._data["sendAt"]
        
    def log_id(self):
        return self._data["logId"]
        
    def author_id(self):
        return self._data["authorId"]
        
    def attachment(self):
        return self._data["attachment"]

    def message(self, encode=True):
        if encode:
            return self._data["message"].encode("utf8")
        else:
            return self._data["message"]
        
    def type(self):
        return self._data["type"]
        
    def prev_id(self):
        return self._data["prevId"]
    
    def chat_id(self):
        return self._data["chatId"]
