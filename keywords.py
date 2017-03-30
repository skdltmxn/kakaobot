# -*- coding: utf-8 -*-

from bot.command import *
import json


class Keyword(object):
    def __init__(self, *args, **kwargs):
        self._keyword = {}
    
    @staticmethod
    def load(cur):
        keyword = Keyword()
        keyword._keyword = {}
        try:
            cur.execute("SELECT data FROM pickled WHERE type = 'keyword';")
            data = cur.fetchone()
            if data is not None:
                unicode_keyword = json.loads(data[0])
                utf8_keyword = {}

                for k, v in unicode_keyword.iteritems():
                    utf8_keyword[k.encode("utf8")] = v.encode("utf8")

                keyword._keyword = utf8_keyword
        except:
            import traceback
            print "---- Keyword.load ----"
            print traceback.format_exc()
            print "-----------------------"

        return keyword

    @staticmethod
    def save(cur, keyword):
        try:
            data = json.dumps(keyword)
            cur.execute("SELECT count(data) FROM pickled WHERE type = 'keyword';")

            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO pickled (type, data) VALUES (%s, %s);", ("keyword", data))
            else:
                cur.execute("UPDATE pickled SET data=(%s) WHERE type=(%s);", (data, "keyword"))
        except:
            import traceback
            print "---- Keyword.save ----"
            print traceback.format_exc()
            print "-----------------------"

    def add(self, key, word):
        self._keyword[key] = word
    
    def remove(self, key):
        del self._keyword[key]

    def get_word(self, key):
        return self._keyword.get(key)

    def keyword(self):
        return self._keyword


class KeywordListOrAddCommand(Command):
    def __init__(self, trigger, keyword):
        super(KeywordListOrAddCommand, self).__init__(trigger)
        self._keyword = keyword

    def description(self):
        return "키워드를 확인하거나 추가한다"

    def usage(self):
        cmd = self.trigger()
        msg = "'/{0}': 전체 키워드 목록을 출력한다\n".format(cmd)
        msg += "'/{0} <키워드>': 특정 키워드를 출력한다\n".format(cmd)
        msg += "'/{0} <키워드> <내용>': <키워드>에 <내용>을 연결한다\n\n".format(cmd)
        msg += "<키워드>는 공백없는 문자열이며 <내용>에은 임의의 문자열을 사용할 수 있습니다\n"
        msg += "<키워드>에는 다음과 같은 특수 형식을 사용할 수 있습니다\n"
        msg += "#sender#: 발신자의 닉네임\n"
        msg += "<키워드>가 이미 존재하는 경우 새로운 <내용>으로 덮어씌워집니다."
        return msg

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()
        keyword = self._keyword.keyword()

        mode = len(args)
        if mode == 0:
            m = "[키워드 목록]\n"
            for key, word in keyword.iteritems():
                m += "{0} => {1}\n".format(key, word)

            m = m[:-1]
            sess.send_text(m, chat_id)
        elif mode == 1:
            key = args[0]
            key = key.replace("\t\r\n", "")
            word = self._keyword.get_word(key)

            if word is not None:
                sess.send_text("{0} => {1}".format(key, word), chat_id)
            else:
                sess.send_text("'{0}' 없는 키워드".format(key), chat_id)
        else:
            key = args.pop(0)
            word = " ".join(args)

            self._keyword.add(key, word)
            sess.send_text("키워드 추가됨".format(key, word), chat_id)


class KeywordRemoveCommand(Command):
    def __init__(self, trigger, keyword):
        super(KeywordRemoveCommand, self).__init__(trigger)
        self._keyword = keyword

    def description(self):
        return "키워드를 제거한다"

    def usage(self):
        cmd = self.trigger()
        msg = "'/{0} <키워드>': 키워드를 삭제한다\n\n".format(cmd)
        msg += "키워드를 삭제하면 더 이상 해당 키워드의 내용이 출력되지 않습니다"
        return msg

    def run(self, sess, args, chat):
        cmd = self.trigger()
        chat_id = chat.chat_id()

        try:
            key = args[0]
            word = self._keyword.get_word(key)

            if word is not None:
                self._keyword.remove(key)
                sess.send_text("'{0}' 삭제 완료".format(key), chat_id)
            else:
                sess.send_text("'{0}' 없는 기억".format(key), chat_id)
        except:
            sess.send_text(self.usage(), chat_id)
