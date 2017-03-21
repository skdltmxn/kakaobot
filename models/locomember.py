# -*- coding: utf-8 -*-


class LocoMember(object):
    def __init__(self, data):
        self._data = data
        
    def status_message(self):
        return self._data["statusMessage"].encode("utf8")
        
    def linked_services(self):
        return self._data["linkedServices"]
        
    def account_id(self):
        return self._data["accountId"]
        
    def type(self):
        return self._data["type"]
        
    def original_profile_img_url(self):
        return self._data["originalProfileImageUrl"]
        
    def full_profile_img_url(self):
        return self._data["fullProfileImageUrl"]
    
    def profile_img_url(self):
        return self._data["profileImageUrl"]
        
    def nickname(self):
        return self._data["nickName"].encode("utf8")
        
    def user_id(self):
        return self._data["userId"]
