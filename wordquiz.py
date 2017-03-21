# -*- coding: utf-8 -*-

import operator
import json
from bot.command import *
from util.utils import *
from random import randint, seed


class QuizException(Exception):
    def __init__(self, msg):
        super(QuizException, self).__init__(msg)
        self._msg = msg

    def why(self):
        return self._msg


class Wordquiz(object):
    CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

    def __init__(self):
        self.new_game()
        self._ranking = {}

    def new_game(self):
        self._playing = False
        self._owner = 0
        self._answer = ""
        self._quiz = ""
        self._voter = []

    @staticmethod
    def load(cur):
        quiz = Wordquiz()
        try:
            cur.execute("SELECT data FROM pickled WHERE type = 'wordquiz';")
            context = json.loads(cur.fetchone()[0])

            quiz._playing = context["playing"]
            quiz._owner = context["owner"]
            quiz._answer = context["answer"].encode("utf8")
            quiz._quiz = context["quiz"].encode("utf8")
            quiz._voter = context["voter"]

            for k, v in context["ranking"].iteritems():
                quiz._ranking[long(k)] = v
        except:
            import traceback
            print "---- Wordquiz.load ----"
            print traceback.format_exc()
            print "-----------------------"

        return quiz

    @staticmethod
    def save(cur, quiz):
        try:
            context = {
                "playing": quiz._playing,
                "owner": quiz._owner,
                "answer": quiz._answer,
                "quiz": quiz._quiz,
                "voter": quiz._voter,
                "ranking": quiz._ranking
            }
            data = json.dumps(context)

            cur.execute("SELECT count(data) FROM pickled WHERE type = 'wordquiz';")

            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO pickled (type, data) VALUES (%s, %s);", ("wordquiz", data))
            else:
                cur.execute("UPDATE pickled SET data=(%s) WHERE type=(%s);", (data, "wordquiz"))
        except:
            import traceback
            print "---- Wordquiz.save ----"
            print traceback.format_exc()
            print "-----------------------"

    @staticmethod
    def _convert(word):
        converted = ""
        answer = ""

        for c in word:
            cc = ord(c)

            if c == " ":
                converted += " "
                answer += " "
                continue
            elif cc < 0xac00 or cc > 0xd7a3:
                continue

            converted += Wordquiz.CHO[(cc - 0xac00) / 588]
            answer += c

        return answer.encode("utf8").strip(), converted

    def start_quiz(self, owner, word):
        if self._playing:
            raise QuizException("이미 퀴즈가 진행중입니다")

        answer, quiz = self._convert(word.decode("utf8"))
        if len(answer) == 0:
            raise QuizException("문제를 제대로 입력하세요")

        self._owner = owner
        self._answer = answer
        self._quiz = quiz
        self._playing = True

        return quiz

    def try_answer(self, answer, user):
        if not self._playing or user == self._owner:
            return False

        if answer == self._answer:
            if user in self._ranking:
                self._ranking[user] += 1
            else:
                self._ranking[user] = 1

            self._playing = False
            return True

        return False

    def owner(self):
        return self._owner

    def quiz(self):
        return self._quiz

    def answer(self):
        return self._answer

    def playing(self):
        return self._playing

    def ranking(self):
        return sorted(self._ranking.items(), key=operator.itemgetter(1), reverse=True)

    def request_impeachment(self, voter):
        try:
            if voter in self._voter:
                raise QuizException("이미 투표했습니다")

            self._voter.append(voter)
        except QuizException:
            raise
        except:
            import traceback
            print traceback.format_exc()

    def voted_count(self):
        return len(self._voter)

    def make_hint(self):
        seed()
        quiz = list(self._quiz.decode("utf8"))
        answer = self._answer.decode("utf8")

        while True:
            idx = randint(0, len(quiz) - 1)
            if quiz[idx] == answer[idx]:
                continue

            quiz[idx] = answer[idx]
            break

        self._quiz = "".join(quiz).encode("utf8")


class WordquizProduceCommand(Command):
    def __init__(self, trigger, wordquiz, quiz_room_id):
        super(WordquizProduceCommand, self).__init__(trigger)
        self._wordquiz = wordquiz
        self._quiz_room_id = quiz_room_id

    def description(self):
        return "자음퀴즈를 출제한다"

    def usage(self):
        m = "'/{0} <문제>': 자음퀴즈를 출제한다\n\n".format(self.trigger())
        m += "<문제>가 자음으로 출제되며 공백도 사용 가능하다"
        return m

    def run(self, sess, args, chat):
        cmd = self.trigger()

        if len(args) < 1:
            sess.send_text(self.usage(), chat_id)
            return

        quiz = " ".join(args)
        chat_id = chat.chat_id()
        author_id = chat.author_id()
        author_nick = sess.get_user_nickname(chat_id, author_id)

        try:
            self._wordquiz.start_quiz(author_id, quiz)

            m = "자음퀴즈를 출제합니다.\n"
            m += "문제: {0}\n".format(self._wordquiz.quiz())
            m += "정답: {0}".format(self._wordquiz.answer())

            sess.send_text(m, chat_id)

            q = "{0}님이 출제하는 자음퀴즈\n".format(author_nick)
            q += "문제: {0}".format(self._wordquiz.quiz())

            sess.send_text(q, self._quiz_room_id)
        except QuizException as e:
            sess.send_text(e.why(), chat_id)
        except Exception as e:
            import traceback
            print traceback.format_exc()


class WordquizInfoCommand(Command):
    def __init__(self, trigger, wordquiz):
        super(WordquizInfoCommand, self).__init__(trigger)
        self._wordquiz = wordquiz

    def description(self):
        return "현재 자음퀴즈 정보를 출력한다"

    def usage(self):
        m = "'/{0}': 현재 자음퀴즈 정보를 출력한다\n\n".format(self.trigger())
        m += "현재 출제중인 문제와 랭킹이 표시된다"
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()

        try:
            quiz = self._wordquiz
            ranking = quiz.ranking()

            if quiz.playing():
                owner_name = sess.get_user_nickname(chat_id, quiz.owner())
                m = "현재 자음퀴즈\n"
                m += "문제: {0}\n".format(quiz.quiz())
                m += "출제자: {0}".format(hide_name(owner_name))

                if quiz.voted_count() > 0:
                    m += "\n탄핵투표수: {0}/5".format(quiz.voted_count())

                sess.send_text(m, chat_id)

            m = "자음퀴즈 랭킹\n"
            n = 1

            for (user, point) in ranking:
                user_name = sess.get_user_nickname(chat_id, user)
                m += "{0}. {1} - {2}점\n".format(n, hide_name(user_name), point)
                n += 1

            m = m[:-1]

            sess.send_text(m, chat_id)
        except:
            import traceback
            print traceback.format_exc()


class WordquizImpeachCommand(Command):
    def __init__(self, trigger, wordquiz):
        super(WordquizImpeachCommand, self).__init__(trigger)
        self._wordquiz = wordquiz

    def description(self):
        return "현재 퀴즈에 대해 탄핵을 요청한다"

    def usage(self):
        m = "'/{0}': 현재 퀴즈에 대해 탄핵을 요청한다\n\n".format(self.trigger())
        m += "5인 이상 요청시 탄핵이 인용된다"
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()
        author = chat.author_id()

        try:
            quiz = self._wordquiz

            if not quiz.playing():
                sess.send_text("출제된 문제가 없습니다", chat_id)
                return

            if quiz.owner() == author:
                sess.send_text("출제자는 요청할 수 없습니다", chat_id)
                return

            quiz.request_impeachment(author)

            sess.send_text("탄핵을 요청했습니다 ({0}/5)".format(quiz.voted_count()), chat_id)

            if quiz.voted_count() > 4:
                owner_name = sess.get_user_nickname(chat_id, quiz.owner())
                m = "주문: 피청구인 {0}의 문제를 파면한다\n".format(owner_name)
                m += "정답: {0}".format(quiz.answer())
                sess.send_text(m, chat_id)
                quiz.new_game()

        except QuizException as e:
            sess.send_text(e.why(), chat_id)
        except:
            import traceback
            print traceback.format_exc()


class WordquizCancelCommand(Command):
    def __init__(self, trigger, wordquiz, quiz_room_id):
        super(WordquizCancelCommand, self).__init__(trigger)
        self._wordquiz = wordquiz
        self._quiz_room_id = quiz_room_id

    def description(self):
        return "현재 진행중인 퀴즈를 취소한다"

    def usage(self):
        m = "'/{0}': 현재 진행중인 퀴즈를 취소한다\n\n".format(self.trigger())
        m += "취소는 출제자만 가능하다"
        return m

    def run(self, sess, args, chat):
        quiz = self._wordquiz
        chat_id = chat.chat_id()
        author = chat.author_id()

        if not quiz.playing():
            sess.send_text("출제된 문제가 없습니다", chat_id)
            return

        if quiz.owner() != author:
            sess.send_text("출제자만 취소할 수 있습니다", chat_id)
            return

        quiz.new_game()
        sess.send_text("출제를 취소했습니다", chat_id)

        owner_name = sess.get_user_nickname(chat_id, author)
        m = "{0}님이 출제를 취소했습니다".format(owner_name)
        sess.send_text(m, self._quiz_room_id)


class WordquizHintCommand(Command):
    def __init__(self, trigger, wordquiz, quiz_room_id):
        super(WordquizHintCommand, self).__init__(trigger)
        self._wordquiz = wordquiz
        self._quiz_room_id = quiz_room_id

    def description(self):
        return "현재 진행중인 퀴즈의 힌트를 제공한다"

    def usage(self):
        m = "'/{0}': 현재 진행중인 퀴즈의 힌트를 제공한다\n\n".format(self.trigger())
        m += "출제자만 제공 가능하며 문제의 글자 중 임의의 한 글자가 공개된다"
        return m

    def run(self, sess, args, chat):
        quiz = self._wordquiz
        chat_id = chat.chat_id()
        author = chat.author_id()

        if not quiz.playing():
            sess.send_text("출제된 문제가 없습니다", chat_id)
            return

        if quiz.owner() != author:
            sess.send_text("출제자만 줄 수 있습니다", chat_id)
            return

        quiz.make_hint()
        sess.send_text("힌트를 공개했습니다", chat_id)

        owner_name = sess.get_user_nickname(chat_id, author)
        m = "{0}님이 힌트를 공개했습니다\n".format(owner_name)
        m += "문제: {0}".format(quiz.quiz())
        sess.send_text(m, self._quiz_room_id)
