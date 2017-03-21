# -*- coding: utf-8 -*-


def hide_name(name):
    name = name.decode("utf8")
    if len(name) > 1:
        name = name.replace(name[1], "*")
        
    return name.encode("utf8")
