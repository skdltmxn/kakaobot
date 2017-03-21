# -*- coding: utf-8 -*-


class Command(object):
    def __init__(self, trigger):
        self._trigger = trigger
        
    def description(self, *args, **kwargs):
        pass
    
    def usage(self, *args, **kwargs):
        pass
        
    def run(self, *args, **kwargs):
        pass

    def trigger(self):
        return self._trigger
