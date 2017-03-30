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

    def get(self, path, **params):
        try:
            data = urlencode(params)
            url = "{0}{1}?{2}".format(self._host, path, data)
            req = urllib2.Request(url, headers=self._headers)
            return json.loads(urllib2.urlopen(req).read())
        except urllib2.HTTPError as e:
            print e.code
            print e.read()

    def post(self, path, **params):
        try:
            data = urlencode(params)
            req = urllib2.Request(self._host + path, data=data, headers=self._headers)
            return json.loads(urllib2.urlopen(req).read())
        except urllib2.HTTPError as e:
            print e.code
            print e.read()
