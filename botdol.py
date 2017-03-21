# -*- coding: utf-8 -*-

import gevent
import pickle
import json
import urlparse
import os
import psycopg2
from util.utils import *
from wordquiz import *
from bot.bot import *
from summary import *
from variable import *
from hangang import *
from help import *
from mafiagame import *
from jeonghan import *
from yamin import *


class Botdol(Bot):
    def __init__(self):
        super(Botdol, self).__init__()
        self._version = 0.6
        self._name = "봇돌이"

        urlparse.uses_netloc.append("postgres")
        url = urlparse.urlparse(os.environ["DATABASE_URL"])

        self._pgconn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        with self._pgconn.cursor() as cursor:
            self._init_db(cursor)
            self._variable = Variable.load(cursor)
            self._wordquiz = Wordquiz.load(cursor)

        self._mafiagame = MafiaGame()

        # 빨래통
        self.add_command(
            111740297355267, VariableListOrAddCommand("ㄱ", self._variable)
        )
        self.add_command(
            111740297355267, VariableRemoveSingleCommand("ㄱㅅ", self._variable)
        )
        self.add_command(
            111740297355267, VariableRemoveAllCommand("ㄱㅈㅅ", self._variable)
        )
        self.add_command(111740297355267, HangangCommand("자살"))
        self.add_command(111740297355267, WordquizInfoCommand("ㅈㅋ", self._wordquiz))
        self.add_command(111740297355267, WordquizImpeachCommand("ㅋㅌ", self._wordquiz))
        self.add_command(111740297355267, SummaryCommand("세줄요약"))
        self.add_command(111740297355267, MafiaCommand("ㅁㅍㅇ", self._mafiagame))
        self.add_command(111740297355267, JeonghanCommand("정한아"))
        self.add_command(111740297355267, YaminCommand("ㅇㅁ"))
        # help must be added at the last
        self.add_command(111740297355267, HelpCommand("?", self._commands.get(111740297355267, {})))

        # 개인톡


        # 그 외
        self.add_command(0, WordquizProduceCommand("ㅈㅋ", self._wordquiz, 111740297355267))
        self.add_command(0, WordquizCancelCommand("ㅋㅊ", self._wordquiz, 111740297355267))
        self.add_command(0, WordquizHintCommand("ㅎㅌ", self._wordquiz, 111740297355267))
        self.add_command(0, MafiaSingleChatCommand("ㅁㅍㅇ", self._mafiagame))
        # help must be added at the last
        self.add_command(0, HelpCommand("?", self._commands.get(0, {})))
        self._bot_timer = gevent.spawn(self._do_timer)

    def _init_db(self, cur):
        cur.execute("""CREATE TABLE IF NOT EXISTS pickled
            (id SERIAL PRIMARY KEY NOT NULL,
             type VARCHAR(12) NOT NULL,
             data TEXT);""")

        self._pgconn.commit()

    def _do_timer(self):
        while True:
            gevent.sleep(60)
            self.save()

    def shutdown(self):
        self._bot_timer.kill()
        self.save()
        self._pgconn.close()

    def save(self):
        with self._pgconn.cursor() as cursor:
            Variable.save(cursor, self._variable.var())
            Wordquiz.save(cursor, self._wordquiz)
            self._pgconn.commit()

    def on_connect(self, sess):
        sess.send_text("{0} v{1} 구동".format(self._name, self._version), 111740297355267)
        sess.send_chat_on_room(111740297355267)

    def on_shutdown(self, sess):
        sess.send_text("{0} v{1} 종료".format(self._name, self._version), 111740297355267)

    def on_msg(self, sess, msg):
        self.process_command(sess, msg)

        author_nick = msg.author()
        msg = msg.chat_log()
        message = msg.message()
        chat_id = msg.chat_id()
        author = msg.author_id()

        # none commands
        if chat_id == 111740297355267:
            if "순복" in message:
                sess.send_text("삐빅! 순복이 감지되었습니다! 발신자: {0}".format(author_nick), chat_id)

            if "정한아" in message:
                sess.send_text("술먹자!", chat_id)

            quiz = self._wordquiz

            if quiz.playing():
                if quiz.try_answer(message, author):
                    sess.send_text("정답! {0}님 1점 획득".format(author_nick), chat_id)
                    quiz.new_game()

        else:
            msg_type = msg.type()
            if msg_type == 1:
                if not message.startswith("/"):
                    sess.send_text(message, 111740297355267)
            # emoticon
            elif msg_type == 12 or msg_type == 20:
                try:
                    emot = json.loads(msg.attachment())
                    path = emot["path"]
                    name = emot["name"]
                    width = emot["width"]
                    height = emot["height"]

                    sess.send_emoticon(message, 111740297355267, msg_type,
                                       path=path,
                                       name=name,
                                       width=width,
                                       height=height
                                       )
                except Exception as e:
                    print e
            # picture
            elif msg_type == 2:
                try:
                    pic = json.loads(msg.attachment())
                    url = pic["url"]
                    w = pic["w"]
                    h = pic["h"]
                    s = pic["s"]
                    mt = pic["mt"]

                    sess.send_picture(message, 111740297355267,
                                      mt=mt,
                                      width=w,
                                      height=h,
                                      path=url.replace("http://dn-m.talk.kakao.com", ""),
                                      localFilePath="/tmp/",
                                      s=s,
                                      type="image/jpeg"
                                      )
                except Exception as e:
                    print str(e)
