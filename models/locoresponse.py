# -*- coding: utf-8 -*-


class LocoResponse(object):
    def __init__(self, data):
        self._data = data
        
    def status(self):
        return self._data["status"]
        
    def error(self):
        return self._data.get("errMsg") or ""
