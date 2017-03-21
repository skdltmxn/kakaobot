# -*- coding: utf-8 -*-


def lookup_error(code):
    if code == 0:
        return "Unknown Error (0)"
    elif code == -100:
        return "Not registered device"
    elif code == -101:
        return "This account is used in another desktop device"
    elif code == -102:
        return "Exceeded device registration limits"
    elif code == -110:
        return "Passcode is expired"
    elif code == -111:
        return "Passcode is incorrect"
    elif code == -120:
        return "Unsupported device version"
    elif code == -910:
        return "Invalid AuthKey"
    elif code == 12:
        return "Incorrect password"
    elif code == 30:
        return "Not registered email"
    elif code == 31:
        return "Not verified email"
    elif code == 32:
        return "Not used in mobile device"
    elif code == 13:
        return "Exceeded login try limits"
    elif code == -998:
        return "Authentication Required"
    elif code == 1000:
        return "Invalid Response Header"
    else:
        return "Unknown Error ({0})".format(code)
