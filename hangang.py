# -*- coding: utf-8 -*-

from bot.command import *
import urllib2
import json


class HangangCommand(Command):
    def description(self):
        return "수월한 자살을 위해 한강 수온을 확인한다"

    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 수월한 자살을 위해 한강 수온을 확인한다\n\n".format(cmd)
        m += "한강 수온은 외부 API를 이용하여 확인하며 온도 갱신은 일정치 않을 수 있습니다"
        return m

    def run(self, sess, args, chat):
        try:
            chat_id = chat.chat_id()

            req = urllib2.urlopen("http://hangang.dkserver.wo.tc", timeout=3)
            data = json.loads(req.read())
            sess.send_text("현재 한강 수온은 {0}°C입니다".format(data["temp"]), chat_id)
        except:
            sess.send_text("요청 실패", chat_id)
