# -*- coding: utf-8 -*-

from urllib import urlencode
import urllib2
import json


class WebClient(object):
    def __init__(self, host):
        self._host = host
        self._headers = {}

    def add_header(self, key, value):
        self._headers[key] = value

    def post(self, path, **params):
        try:
            data = urlencode(params)
            req = urllib2.Request(self._host + path, data=data, headers=self._headers)
            return json.loads(urllib2.urlopen(req).read())
        except urllib2.HTTPError as e:
            print e.code
            print e.read()
