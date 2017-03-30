# -*- coding: utf-8 -*-

import operator
from bot.command import *
from util.utils import *


class ShareCommand(Command):
    def __init__(self, trigger):
        super(ShareCommand, self).__init__(trigger)
        self._delta = 8388899092

    def description(self):
        return "과거 대화에 대한 지분을 출력한다"

    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 과거 3시간 전까지 대화의 지분을 출력한다\n".format(cmd)
        m += "'/{0}' <시간>: 과거 대화의 지분을 출력한다\n\n".format(cmd)
        m += "<시간>은 1 ~ 24까지의 값을 가지며 단위는 시간이다\n"
        m += "ex) '/{0} 5': 5시간 전까지 대화의 지분을 출력한다".format(cmd)
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()

        # default from last 3 hours
        if len(args) < 1:
            hour = 3
        else:
            try:
                hour = int(args[0])
                if hour < 1 or hour > 24:
                    raise ValueError()
            except ValueError:
                sess.send_text("1 ~ 24(시간) 사이로만 입력하세요", chat_id)
                return

        last_log_id = chat.log_id()
        since = last_log_id - (self._delta * 60  * 60 * hour)

        logs = sess.send_mchat_logs(chat_id, since)
        chat_logs = logs.chat_logs()

        freqmap = {}
        chat_count = 0

        while True:
            for chat in chat_logs:
                if chat.author_id() == sess.my_user_id():
                    continue

                length = len(chat.message(False))
                freqmap[chat.author_id()] = freqmap.get(chat.author_id(), 0) + length
                chat_count += length

            if logs.eof():
                break

            logs = sess.send_mchat_logs(chat_id, chat_logs[len(chat_logs) - 1].log_id())
            chat_logs = logs.chat_logs()

        share_list = sorted(freqmap.items(), key=operator.itemgetter(1), reverse=True)

        m = "대화 지분\n"
        i = 1
        for user, cnt in share_list:
            nickname = sess.get_user_nickname(chat_id, user)
            m += "{}. {} ({:.2f}%)\n".format(i, hide_name(nickname), float(cnt) / chat_count * 100)
            i += 1

        sess.send_text(m.rstrip(), chat_id)
