# -*- coding: utf-8 -*-

from bot.command import *
from datetime import datetime
from time import mktime
import pytz
import json


class Dday(object):
    def __init__(self, *args, **kwargs):
        self._dday = {}

    @staticmethod
    def load(cur):
        dday = Dday()
        try:
            cur.execute("SELECT data FROM pickled WHERE type = 'dday';")
            fetched = cur.fetchone()
            if fetched is None:
                dday._dday = {}
            else:
                unicode_dday = json.loads(fetched[0])
                utf8_dday = {}

                for k, v in unicode_dday.iteritems():
                    utf8_dday[k.encode("utf8")] = v

                dday._dday = utf8_dday

            return dday
        except:
            import traceback
            print "------ Dday.load ------"
            print traceback.format_exc()
            print "-----------------------"

    @staticmethod
    def save(cur, dday):
        try:
            data = json.dumps(dday)
            cur.execute("SELECT count(data) FROM pickled WHERE type = 'dday';")

            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO pickled (type, data) VALUES (%s, %s);", ("dday", data))
            else:
                cur.execute("UPDATE pickled SET data=(%s) WHERE type=(%s);", (data, "dday"))
        except:
            import traceback
            print "------ Dday.save ------"
            print traceback.format_exc()
            print "-----------------------"

    def get_timestamp(self, name):
        return self._dday.get(name)

    def add(self, name, timestamp):
        self._dday[name] = timestamp

    def remove(self, name):
        del self._dday[name]

    def dday(self):
        return self._dday

class DdayListOrAddCommand(Command):
    def __init__(self, trigger, dday):
        super(DdayListOrAddCommand, self).__init__(trigger)
        self._dday = dday
        self._tz = pytz.timezone('Asia/Seoul')

    def description(self):
        return "디데이를 확인하거나 추가한다"

    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 저장된 디데이를 출력한다\n\n".format(cmd)
        m += "'/{0} <디데이>': 특정 디데이를 출력한다\n".format(cmd)
        m += "'/{0} <디데이> <날짜>': <디데이>에 <날짜>를 입력한다\n\n".format(cmd)
        m += "<디데이>에는 임의의 값을 입력할 수 있으며 <날짜>는 반드시 YYYYMMDD 형식으로 입력해야 합니다"
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()
        dday = self._dday
        tz = self._tz
        today = datetime.now(tz)
        alarm_days = []

        mode = len(args)
        if mode == 0:

            m = "[디데이 목록]\n"
            for k, v in dday.dday().iteritems():
                d = datetime.fromtimestamp(v, tz=tz)
                delta = (today - d).days
                if delta == 0:
                    alarm_days.append(k)

                m += "{0} = {1}-{2:02}-{3:02} (D{4:+})\n".format(k, d.year, d.month, d.day, delta)

            m = m[:-1]
            sess.send_text(m, chat_id)

            for d in alarm_days:
                m = "☆★☆★☆★☆★경☆★☆★☆★☆★축☆★☆★☆★☆★\n"
                m += "오늘은 기다리고 기다리던 '{0}'입니다!!\n".format(d)
                m += "☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★"
                sess.send_text(m, chat_id)

        elif mode == 1:
            name = args[0].replace("\t\r\n", " ")
            timestamp = dday.get_timestamp(name)

            if timestamp is not None:
                d = datetime.fromtimestamp(timestamp, tz=tz)
                delta = (today - d).days
                if delta == 0:
                    alarm_days.append(name)
                m = "{0} = {1}-{2:02}-{3:02} (D{4:+})".format(name, d.year, d.month, d.day, delta)
                sess.send_text(m, chat_id)

                for d in alarm_days:
                    m = "☆★☆★☆★경☆★☆★☆★축☆★☆★☆★\n"
                    m += "오늘은 기다리고 기다리던 '{0}'입니다!!\n".format(d)
                    m += "☆★☆★☆★☆★☆★☆★☆★☆★☆★☆★"
                    sess.send_text(m, chat_id)

            else:
                sess.send_text("'{0}' 없는 디데이".format(var), chat_id)
        else:
            target_day = args[-1]
            try:
                if len(target_day) != 8:
                    raise

                year = int(target_day[:4])
                month = int(target_day[4:6])
                day = int(target_day[6:8])

                d = datetime(year, month, day, tzinfo=tz)
                timestamp = int(mktime(d.timetuple()))
                name = " ".join(args[:-1])
                dday.add(name, timestamp)

                sess.send_text("디데이 '{0}' 추가됨".format(name), chat_id)
            except:
                sess.send_text("날짜는 YYYYMMDD 형식이어야 합니다", chat_id)
                return


class DdayRemoveCommand(Command):
    def __init__(self, trigger, dday):
        super(DdayRemoveCommand, self).__init__(trigger)
        self._dday = dday

    def description(self):
        return "디데이를 삭제한다"

    def usage(self):
        cmd = self.trigger()
        msg = "'/{0} <디데이>': 디데이를 삭제한다\n\n".format(cmd)
        msg += "<디데이>에 저장된 내용을 삭제합니다."
        return msg

    def run(self, sess, args, chat):
        cmd = self.trigger()
        chat_id = chat.chat_id()
        dday = self._dday

        if len(args) < 1:
            sess.send_text(self.usage(), chat_id)
            return

        name = " ".join(args)

        if dday.get_timestamp(name) is not None:
            self._dday.remove(name)
            sess.send_text("'{0}' 삭제 완료".format(name), chat_id)
        else:
            sess.send_text("'{0}' 없는 디데이".format(name), chat_id)
