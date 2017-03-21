# -*- coding: utf-8 -*-

from bot.command import *


class JeonghanCommand(Command):
    def description(self):
        return "정한이에게 술을 권한다"

    def usage(self):
        m = "'/{0}': 정한이에게 술을 권한다\n\n".format(self.trigger())
        m += "하지만 정한이가 응하는 경우는 없다"
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()

        sess.send_text("술먹자!", chat_id)
