# -*- coding: utf-8 -*-

from locorequest import LocoRequest


class LocoMemberRequest(LocoRequest):
    def method(self):
        return "MEMBER"
