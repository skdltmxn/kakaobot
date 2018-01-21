# -*- coding: utf-8 -*-

import operator
import re
from bot.command import *


class SummaryCommand(Command):
    def __init__(self, trigger):
        super(SummaryCommand, self).__init__(trigger)
        self._delta = 8388899092
        self._blacklist = [u"그래서", u"아니냐"]

    def description(self):
        return "과거 대화를 세 줄로 요약한다"

    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 과거 3시간 전까지 대화를 세 줄로 요약한다\n".format(cmd)
        m += "'/{0}' <시간>: 과거 대화를 세 줄로 요약한다\n\n".format(cmd)
        m += "<시간>은 1 ~ 24까지의 값을 가지며 단위는 시간이다\n"
        m += "ex) '/{0} 5': 5시간 전까지 대화를 요약한다".format(cmd)
        return m

    def _filter(self, word):
        if len(word) < 3:
            return True

        if word.startswith("/"):
            return True

        if re.match(ur"^[\u3131-\u314e]+$", word, re.UNICODE) is not None:
            return True

        if word in self._blacklist:
            return True

        return False

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

        while True:
            for chat in chat_logs:
                if chat.author_id() == sess.my_user_id():
                    continue

                msg = chat.message(False)
                if msg.startswith("/"):
                    continue
                
                words = msg.split()
                for word in words:
                    if self._filter(word):
                        continue

                    freqmap[word] = freqmap.get(word, 0) + 1

            if logs.eof():
                break

            logs = sess.send_mchat_logs(chat_id, chat_logs[len(chat_logs) - 1].log_id())
            chat_logs = logs.chat_logs()

        summary = sorted(freqmap.items(), key=operator.itemgetter(1), reverse=True)[:3]

        m = "세줄요약\n"
        m += "1. {0} ({1}회)\n".format(summary[0][0].encode("utf8"), summary[0][1])
        m += "2. {0} ({1}회)\n".format(summary[1][0].encode("utf8"), summary[1][1])
        m += "3. {0} ({1}회)".format(summary[2][0].encode("utf8"), summary[2][1])

        sess.send_text(m, chat_id)
