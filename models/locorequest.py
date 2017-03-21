# -*- coding: utf-8 -*-


class LocoRequest(object):
    def __init__(self, **kwargs):
        self._data = kwargs

    def method(self):
        pass

    def data(self):
        return self._data
