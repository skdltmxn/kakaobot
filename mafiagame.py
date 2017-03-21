# -*- coding: utf-8 -*-

import gevent
from gevent import Timeout
from gevent.event import Event
import pickle
import time
import operator
from bot.command import *
from util.utils import *
from random import randint, seed, shuffle


class GameException(Exception):
    def __init__(self, msg):
        super(GameException, self).__init__(msg)
        self._msg = msg

    def why(self):
        return self._msg

"""
class MafiaJob(object):
    def __init__(self):
        pass

    def job(self):
        pass

    def do_job(self):
        pass

class MafiaJobMafia(MafiaJob):
    def __init__(self, chat_id):


    def job(self):
        return "마피아"

    def do_job(self):

class MafiaJobCivilian(MafiaJob):
    def job(self):
        return "시민"
"""

class MafiaGame(object):
    SAVEFILE = "bot_mafia"
    VERSION = 0.5

    JOB_MAFIA = "마피아"
    JOB_POLICE = "경찰"
    JOB_CIVIL = "시민"

    STATE_IDLE = 0
    STATE_WAITING = 1
    STATE_DAY = 2
    STATE_FINAL_STMT = 3
    STATE_NIGHT = 4

    @staticmethod
    def load():
        try:
            with open(MafiaGame.SAVEFILE, "rb") as f:
                return pickle.load(f)
        except:
            return MafiaGame()

    @staticmethod
    def save(game):
        try:
            with open(MafiaGame.SAVEFILE, "wb") as f:
                return pickle.dump(game, f)
        except Exception as e:
            print "Failed to save MafiaGame: {0}".format(str(e))

    @staticmethod
    def rule(cmd):
        m = "게임은 최초 방장이 '/{0} 뉴방' 명령어을 사용함과 동시에 시작된다\n".format(cmd)
        m += "그 후 나머지 인원은 30분 안에 '/{0} 참가' 명령어를 입력해야 게임에 참가할 수 있다\n".format(cmd)
        m += "참가 최소 인원은 4명이며 30분이 지나거나 방장이 게임을 시작하면 게임이 본격적으로 시작된다\n"
        m += "직업은 마피아, 시민으로 구성되며 마피아 선정 시 대상자에게 개인톡으로 알려준다\n"
        m += "낮 시간에 '/{0} 지목 <번호>' 명령어를 통해 용의자를 지목할 수 있으며\n".format(cmd)
        m += "지목된 용의자의 최종변론 후 다시 '/{0} 찬성' 혹은 '/{0} 반대' 명령어로 사형투표를 진행한다\n".format(cmd)
        m += "용의자 지목은 모든 인원이 지목하거나 30분이 지나면 마무리되며 지목에 참가하지 않은 인원은 사형투표를 할 수 없다\n"
        m += "용의자 지목은 다수결의 원칙에 의해 진행되며 과반수가 넘지 않을 경우 최대 2회 재투표를 진행한다\n"
        m += "사형투표는 다수결의 원칙에 의해 진행되며 동률인 경우 최대 2회 재투표를 진행한다\n"
        m += "모든 투표는 총 3번까지 결과가 나오지 않으면 아무도 죽지 않고 밤 시간으로 넘어간다\n"
        m += "밤 시간에는 먼저 마피아들이 '/{0} 지목 <번호>' 명령어로 제거할 사람을 지목한다\n".format(cmd)
        m += "지목은 낮과 마찬가지로 최장 30분간 진행되며 동률인 경우 지목된 사람 중 랜덤으로 1명이 죽는다\n"
        #m += "마피아의 지목이 끝난 후 경찰은 역시 같은 명령어로 한 사람이 마피아인지 여부를 알아낼 수 있다\n"
        m += "다시 낮이 되면 결과가 발표되고 용의자 지목이 반복된다"
        return m


    def __init__(self):
        self.new_game()

    def _set_state(self, state, limit):
        self._state = state
        self._time_limit = int(time.time()) + limit

    def new_game(self):
        seed()
        self._players = []
        self._mafias = []
        self._mafia_rooms = []
        self._livings = []
        self._deads = []
        self._suspect_voters = []
        self._suspect_votes = {}
        self._kill_voters = []
        self._kill_votes = (0, 0)
        self._mafia_voters = []
        self._mafia_votes = {}
        self._vote_try = 0
        self._suspect = 0
        self._owner = 0
        self._status = {}
        self._state = self.STATE_IDLE
        self._event = None
        self._last_time = time.time()

    def players(self):
        return self._players

    def mafias(self):
        return self._mafias

    def deads(self):
        return self._deads

    def livings(self):
        return self._livings

    def owner(self):
        return self._owner

    def state(self):
        return self._state

    def wait_players(self, author):
        self._set_state(self.STATE_WAITING, 60 * 30)
        self._owner = author
        self.participate(author)
        self._event = Event()

        try:
            # wait for 30 minutes
            self._event.wait(timeout=Timeout(60 * 30))
        except Timeout:
            pass

    def participate(self, author):
        if self._state != self.STATE_WAITING:
            raise GameException("참가할 때가 아닙니다")

        if author in self._players:
            raise GameException("이미 참가했습니다")

        self._players.append(author)

    def start(self):
        shuffle(self._players)

        n_mafia = int(round(float(len(self._players)) / 4))

        for i in range(0, n_mafia):
            self._mafias.append(self._players[i])

        shuffle(self._players)
        self._livings = list(self._players)

    def set_event(self):
        if self._event is not None:
            self._event.set()

    def last_time(self):
        return self._last_time

    def time_left(self):
        diff = self._time_limit - int(time.time())

        if diff < 0:
            diff = 0

        return diff

    def suspect_voters(self):
        return self._suspect_voters

    def kill_voters(self):
        return self._kill_voters

    def set_mafia_rooms(self, rooms):
        self._mafia_rooms = rooms

    def mafia_rooms(self):
        return self._mafia_rooms

    def suspect(self):
        return self._suspect

    def start_day(self):
        self._set_state(self.STATE_DAY, 60 * 30) # TEST
        self._suspect_votes = {}
        self._suspect_voters = []
        self._vote_try = 1

    def start_final_stmt(self):
        self._set_state(self.STATE_FINAL_STMT, 60 * 10) # TEST
        self._kill_votes = (0, 0)
        self._kill_voters = []
        self._vote_try = 1

    def start_night(self):
        self._set_state(self.STATE_NIGHT, 60 * 30) # TEST
        self._mafia_voters = []
        self._mafia_votes = {}
        self._suspect = 0

    def vote_for_suspect(self, voter, idx):
        if self._state == self.STATE_IDLE or self._state == self.STATE_WAITING:
            raise GameException("게임이 시작되지 않았습니다")

        if voter not in self._players:
            raise GameException("게임에 참가 중이 아닙니다")

        if voter not in self._livings:
            raise GameException("죽은 자는 관여할 수 없습니다")

        if self._state != self.STATE_DAY:
            raise GameException("용의자를 지목할 시간이 아닙니다")

        if voter in self._suspect_voters:
            raise GameException("이미 지목했습니다")

        self._suspect_votes[self._livings[idx]] = self._suspect_votes.get(self._livings[idx], 0) + 1
        self._suspect_voters.append(voter)

    def suspect_vote_count(self, player):
        return self._suspect_votes.get(player, 0)

    def can_pick_suspect(self):
        if len(self._suspect_voters) == len(self._livings):
            return True

        sorted_vote = sorted(self._suspect_votes.items(), key=operator.itemgetter(1), reverse=True)
        threshold = len(self._livings) / 2 + 1

        if sorted_vote[0][1] >= threshold:
            return True

        return False

    def retry_suspect_vote(self):
        self._suspect_voters = []
        self._suspect_votes = {}
        self._vote_try += 1

        return self._vote_try

    def pick_suspect(self):
        sorted_vote = sorted(self._suspect_votes.items(), key=operator.itemgetter(1), reverse=True)
        threshold = len(self._livings) / 2 + 1

        if len(self._suspect_voters) < threshold:
            return 0

        max_vote = 0
        for target, votes in sorted_vote:
            if votes == max_vote:
                return 0

            max_vote = max(max_vote, votes)

        self._suspect = sorted_vote[0][0]
        return self._suspect

    def release_suspect(self):
        self._suspect = 0

    def vote_for_kill(self, voter, kill):
        if self._state == self.STATE_IDLE or self._state == self.STATE_WAITING:
            raise GameException("게임이 시작되지 않았습니다")

        if voter not in self._players:
            raise GameException("게임에 참가 중이 아닙니다")

        if voter not in self._livings:
            raise GameException("죽은 자는 관여할 수 없습니다")

        if self._state != self.STATE_FINAL_STMT:
            raise GameException("지목된 용의자가 없습니다")

        if voter == self._suspect:
            raise GameException("본인은 투표할 수 없습니다")

        if voter in self._kill_voters:
            raise GameException("이미 투표했습니다")

        (yes, no) = self._kill_votes
        if kill:
            self._kill_votes = (yes + 1, no)
        else:
            self._kill_votes = (yes, no + 1)

        self._kill_voters.append(voter)

    def can_determine_kill(self):
        (yes, no) = self._kill_votes

        maximum = len(self._livings) - 1
        if (yes + no) == maximum:
            return True

        threshold = maximum / 2 + 1

        if yes >= threshold or no >= threshold:
            return True

        return False

    def kill_votes(self):
        return self._kill_votes

    def retry_kill_vote(self):
        self._kill_votes = (0, 0)
        self._kill_voters = []
        self._vote_try += 1

    def kill_player(self, player):
        if player not in self._livings:
            raise GameException("잘못된 타겟")

        self._livings.remove(player)
        if player in self._mafias:
            i = self._mafias.index(player)
            self._mafias.pop(i)
            self._mafia_rooms.pop(i)

        self._deads.append(player)

    def get_job(self, player):
        if player in self._mafias:
            return self.JOB_MAFIA
        else:
            return self.JOB_CIVIL

    def check_victory(self):
        n_mafia = len(self._mafias)
        n_civil = len(self._livings) - n_mafia

        if n_mafia == 0:
            return (True, self.JOB_CIVIL)
        elif n_mafia >= n_civil:
            return (True, self.JOB_MAFIA)
        else:
            return (False, "")

    def vote_by_mafia(self, voter, idx, chat_id):
        if voter in self._mafia_voters:
            raise GameException("이미 투표했습니다")

        if chat_id not in self._mafia_rooms:
            raise GameException("마피아가 아닙니다")

        target = self._livings[idx]
        self._mafia_votes[target] = self._mafia_votes.get(target, 0) + 1
        self._mafia_voters.append(voter)

    def mafia_voters(self):
        return self._mafia_voters

    def pick_mafia_target(self):
        sorted_vote = sorted(self._mafia_votes.items(), key=operator.itemgetter(1), reverse=True)

        if len(sorted_vote) == 0:
            return 0

        pick_list = []
        max_vote = sorted_vote[0][1]

        for target, votes in sorted_vote:
            if votes == max_vote:
                pick_list.append(target)
            else:
                break

        return pick_list[randint(0, len(pick_list) - 1)]


class MafiaCommand(Command):
    def __init__(self, trigger, game):
        super(MafiaCommand, self).__init__(trigger)
        self._game = game

    def description(self):
        return "마피아 게임과 관련된 명령어"

    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 현재 게임 정보를 출력한다\n".format(cmd)
        m += "'/{0} 뉴방': 새로운 마피아 방을 개설한다\n".format(cmd)
        m += "'/{0} 시작': 마피아 게임을 시작한다\n".format(cmd)
        m += "'/{0} 참가': 게임이 시작되었을 경우 참가한다\n".format(cmd)
        m += "'/{0} 지목 <번호>': 게임 중 재판에 회부할 사람을 투표한다\n".format(cmd)
        m += "'/{0} 찬성': 최종변론한 사람을 죽이는 데 찬성한다\n".format(cmd)
        m += "'/{0} 반대': 최종변론한 사람을 죽이는 데 반대한다\n".format(cmd)
        m += "'/{0} 규칙': 게임의 상세한 규칙을 확인한다\n\n".format(cmd)
        m += "상세한 규칙과 명령어 사용 예는 '/{0} 규칙' 명령어를 통해 확인이 가능하다\n".format(cmd)
        m += "가급적 게임을 시작하기 전에 규칙을 숙지하는 것이 바람직하다"
        return m

    def _game_timer(self, sess, chat_id):
        game = self._game

        def before_night(sess, chat_id, game):
            m = "밤이 되었습니다\n"
            m += "마피아들은 개인톡을 통해 제거할 사람을 지목해주세요"
            sess.send_text(m, chat_id)

            game.start_night()
            m = "제거 대상을 지목해주세요\n"
            m += "현재 생존자 목록\n"
            for i, player in zip(range(0, len(game.livings())), game.livings()):
                m += "{0}. {1}\n".format(i, hide_name(sess.get_user_nickname(chat_id, player)))

            for room in game.mafia_rooms():
                sess.send_text(m.strip(), room)

        def _check_victory(sess, chat_id, game):
            (finished, winner) = game.check_victory()
            if finished:
                m = "게임 종료\n"
                m += "승리팀: {0}\n".format(winner)
                m += "--- 생존자 목록 ---\n"
                for player in game.livings():
                    player_name = sess.get_user_nickname(chat_id, player)
                    player_job = game.get_job(player)
                    m += "{0} / {1}\n".format(player_name, player_job)

                sess.send_text(m.strip(), chat_id)
                game.new_game()

            return finished

        while True:
            state = game.state()
            diff = game.time_left()

            if state == game.STATE_DAY:
                if diff == 0 or game.can_pick_suspect():
                    suspect = game.pick_suspect()
                    if suspect == 0:
                        m = "용의자 지목에 실패했습니다 (동률 혹은 과반수 미만)\n"

                        if game.retry_suspect_vote() > 3:
                            m += "총 3번 용의자가 지목되지 않아 밤이 되었습니다"
                            sess.send_text(m, chat_id)
                            before_night(sess, chat_id, game)
                        elif diff == 0:
                            m += "시간 제한이 끝나 밤으로 넘어갑니다"
                            sess.send_text(m, chat_id)
                            before_night(sess, chat_id, game)
                        else:
                            m += "다시 지목하시길 바랍니다"
                            sess.send_text(m, chat_id)

                    else:
                        m = "용의자 {0}님은 최종변론을 시작하세요\n".format(sess.get_user_nickname(chat_id, suspect))
                        m += "나머지 인원은 투표를 시작하세요"
                        sess.send_text(m, chat_id)
                        game.start_final_stmt()

                    continue
            elif state == game.STATE_FINAL_STMT:
                if diff == 0 or game.can_determine_kill():
                    (yes, no) = game.kill_votes()
                    if yes == no:
                        m = "용의자 사형이 부결되었습니다\n"
                        if game.retry_kill_vote() > 3:
                            m += "총 3번 사형이 부결되어 밤으로 넘어갑니다"
                            sess.send_text(m, chat_id)
                        elif diff == 0:
                            m += "시간 제한이 끝나 밤으로 넘어갑니다"
                            sess.send_text(m, chat_id)
                        else:
                            m += "다시 투표해주시기 바랍니다"
                            sess.send_text(m, chat_id)
                            continue
                    elif yes > no:
                        suspect_job = game.get_job(game.suspect())
                        suspect_name = sess.get_user_nickname(chat_id, game.suspect())
                        m = "투표 결과: {0}({1})님을 사형합니다".format(suspect_name, suspect_job)
                        sess.send_text(m, chat_id)
                        game.kill_player(game.suspect())
                        if _check_victory(sess, chat_id, game):
                            continue
                    else:
                        m = "투표 결과: 용의자 {0}님을 석방합니다".format(sess.get_user_nickname(chat_id, game.suspect()))
                        sess.send_text(m, chat_id)
                        game.release_suspect()

                    before_night(sess, chat_id, game)
                    continue
            elif state == game.STATE_NIGHT:
                if diff == 0 or len(game.mafia_voters()) == len(game.mafias()):
                    target = game.pick_mafia_target()
                    if target == 0:
                        sess.send_text("밤 사이 아무 일도 일어나지 않았습니다", chat_id)
                    else:
                        game.kill_player(target)
                        m = "{0}님이 쥐도새도 모르게 처리됐습니다".format(sess.get_user_nickname(chat_id, target))
                        sess.send_text(m, chat_id)
                        if _check_victory(sess, chat_id, game):
                            continue

                    m = "날이 밝았습니다!\n"
                    m += "살아남은 사람들은 토론을 계속해주세요"
                    sess.send_text(m, chat_id)
                    game.start_day()
                    continue
            else:
                break

            gevent.sleep(1.0)

    def run(self, sess, args, chat):
        mode = len(args)
        chat_id = chat.chat_id()
        author = chat.author_id()
        game = self._game
        cmd = self.trigger()

        if mode == 0:
            def format_time(diff):
                if diff < 60:
                    return "{0}초".format(diff)
                else:
                    return "{0}분 {1}초".format(diff / 60, diff % 60)

            state = game.state()

            m = "마피아 v{0}\n\n".format(MafiaGame.VERSION)

            if state == game.STATE_IDLE:
                m += "개설된 방이 없습니다\n"
                m += "'/{0} 뉴방' 명령어로 방을 만드세요".format(cmd)
            elif state == game.STATE_WAITING:
                m += "참가 대기중\n"
                m += "남은 시간: {0}\n".format(format_time(game.time_left()))
                m += "현재 참가 인원\n"
                m += "[*] {0}\n".format(hide_name(sess.get_user_nickname(chat_id, game.owner())))

                for player in game.players()[1:]:
                    m += "[-] {0}\n".format(hide_name(sess.get_user_nickname(chat_id, player)))
            elif state == game.STATE_DAY:
                m += "용의자 지목 중 ({0}/{1})\n".format(len(game.suspect_voters()), len(game.livings()))
                for i, player in zip(range(0, len(game.livings())), game.livings()):
                    m += "{0} - {1} ({2}표)\n".format(i, hide_name(sess.get_user_nickname(chat_id, player)), game.suspect_vote_count(player))

                m += "남은 시간: {0}".format(format_time(game.time_left()))
            elif state == game.STATE_FINAL_STMT:
                suspect_name = hide_name(sess.get_user_nickname(chat_id, game.suspect()))
                (yes, no) = game.kill_votes()
                m += "용의자 {0} 사형 투표 중\n".format(suspect_name)
                m += "찬성: {0}표 / 반대: {1}표\n".format(yes, no)
                m += "남은 시간: {0}".format(format_time(game.time_left()))
            elif state == game.STATE_NIGHT:
                m += "마피아 활동 중\n"
                m += "남은 시간: {0}\n".format(format_time(game.time_left()))
                m += "현재 생존자 목록\n"
                for i, player in zip(range(0, len(game.livings())), game.livings()):
                    m += "{0}. {1}\n".format(i, hide_name(sess.get_user_nickname(chat_id, player)))

            sess.send_text(m.strip(), chat_id)
        elif mode == 1:
            sub_cmd = args[0]

            if sub_cmd == "뉴방":
                if game.state() != game.STATE_IDLE:
                    owner = sess.get_user_nickname(chat_id, game.owner())
                    sess.send_text("이미 방이 있습니다. 방장: {0}".format(hide_name(owner)), chat_id)
                    return

                game.new_game()
                waiter = gevent.spawn(game.wait_players, author)
                owner = sess.get_user_nickname(chat_id, author)
                m = "새로운 마피아 게임 (방장: {0})\n".format(owner)
                m += "30분 후 자동 시작"
                sess.send_text(m, chat_id)

                waiter.join()

                if len(game.players()) < 4:
                    game.new_game()
                    sess.send_text("최소 참가 인원이 충족되지 못해 방을 폭파합니다", chat_id)
                    return

                game.start()
                m = "마피아 게임을 시작합니다!\n"
                m += "---- 생존자 목록 ----\n"
                for i, player in zip(range(0, len(game.livings())), game.livings()):
                    m += "{0}. {1}\n".format(i, sess.get_user_nickname(chat_id, player))

                sess.send_text(m, chat_id)

                mafias = game.mafias()
                mafia_rooms = []
                mafia_names = ", ".join([sess.get_user_nickname(chat_id, x) for x in mafias])
                for player in game.players():
                    room = sess.send_create(player)
                    try:
                        m = "게임이 시작됐습니다\n"
                        if player in mafias:
                            mafia_rooms.append(room.chat_id())
                            m = "당신은 마피아입니다\n"
                            m += "정체를 숨기고 시민들을 제거하세요"
                            if len(mafias) > 1:
                                m += "\n이번 게임의 마피아는 {0}입니다".format(mafia_names)
                        else:
                            m = "당신은 시민입니다\n"
                            m += "마피아를 모두 찾아내 제거하세요"

                        sess.send_text(m, room.chat_id())
                    except:
                        import traceback
                        print traceback.format_exc()

                game.set_mafia_rooms(mafia_rooms)
                game.start_day()
                gevent.spawn(self._game_timer, sess, chat_id)

            elif sub_cmd == "시작":
                if author == game.owner():
                    n_players = len(game.players())
                    if n_players < 4:
                        m = "최소 참가 인원은 4명입니다\n"
                        m += "현재 참가 인원: {0}명".format(n_players)
                        sess.send_text(m, chat_id)
                        return

                    game.set_event()
                else:
                    sess.send_text("방장이 아닙니다", chat_id)

            elif sub_cmd == "참가":
                try:
                    game.participate(author)
                    sess.send_text("게임에 참가합니다. 현재 {0}명".format(len(game.players())), chat_id)
                except GameException as e:
                    sess.send_text(e.why(), chat_id)
                except:
                    raise

            elif sub_cmd == "찬성":
                try:
                    game.vote_for_kill(author, True)
                    sess.send_text("용의자 사형에 찬성했습니다", chat_id)
                except GameException as e:
                    sess.send_text(e.why(), chat_id)
                except:
                    raise
            elif sub_cmd == "반대":
                try:
                    game.vote_for_kill(author, False)
                    sess.send_text("용의자 사형에 반대했습니다", chat_id)
                except GameException as e:
                    sess.send_text(e.why(), chat_id)
                except:
                    raise
            elif sub_cmd == "규칙":
                sess.send_text(MafiaGame.rule(cmd), chat_id)
            else:
                sess.send_text(self.usage(), chat_id)
        elif mode == 2:
            sub_cmd = args.pop(0)

            if sub_cmd == "지목":
                try:
                    idx = int(args[0])

                    game.vote_for_suspect(author, idx)
                    sess.send_text("용의자를 지목했습니다", chat_id)
                except GameException as e:
                    sess.send_text(e.why(), chat_id)
                except:
                    sess.send_text("지목할 용의자 번호가 올바르지 않습니다", chat_id)
            else:
                sess.send_text(self.usage(), chat_id)


class MafiaSingleChatCommand(Command):
    def __init__(self, trigger, game):
        super(MafiaSingleChatCommand, self).__init__(trigger)
        self._game = game

    def description(self):
        return "마피아 게임과 관련된 명령어"

    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 현재 게임과 내 정보를 출력한다\n".format(cmd)
        m += "'/{0} 지목 <번호>': 마피아인 경우 밤에 제거할 사람을 지목한다\n\n".format(cmd)
        m += "이 명령어는 개인톡에서만 사용할 수 있는 마피아 명령어이다"
        return m

    def run(self, sess, args, chat):
        mode = len(args)
        chat_id = chat.chat_id()
        author = chat.author_id()
        game = self._game
        cmd = self.trigger()

        if mode == 0:
            state = game.state()

            m = "마피아 v{0}\n\n".format(MafiaGame.VERSION)

            if state == game.STATE_IDLE:
                m += "진행중인 게임이 없습니다"
                sess.send_text(m, chat_id)
            elif state == game.STATE_WAITING:
                if author in game.players():
                    m += "게임에 참가하기로 했습니다\n"
                    m += "게임이 시작될 떄까지 기다려주세요"
                else:
                    m += "현재 참가 인원 모집중입니다\n"
                    m += "단톡방에서 게임에 참가하세요"

                sess.send_text(m, chat_id)
            else:
                if author not in game.players():
                    m += "게임에 참가 중이지 않습니다"
                    sess.send_text(m, chat_id)
                    return

                if author in game.deads():
                    m += "죽은 자는 관여할 수 없습니다"
                    sess.send_text(m, chat_id)
                    return

                my_job = game.get_job(author)

                m += "당신은 {0}입니다\n".format(my_job)

                if state == game.STATE_DAY:

                    if my_job == game.JOB_MAFIA:
                        m += "시민들이 당신의 정체를 알아채지 못하도록 하세요\n"
                    else:
                        m += "정체를 숨기고 있는 마피아를 찾아 제거하세요\n"
                elif state == game.STATE_FINAL_STMT:
                    if game.suspect() == author:
                        m += "당신은 용의자로 지목됐습니다\n"
                        m += "사형만은 면할 수 있도록 최선을 다하세요\n"
                    else:
                        m += "지목된 용의자를 사형시킬지 투표하세요\n"
                        m += "게임의 승패가 걸린 문제이니 신중하게 생각하세요\n"
                elif state == game.STATE_NIGHT:
                    if my_job == game.JOB_MAFIA:
                        m += "당신은 마피아로서 이 밤에 제거할 인원을 지목할 수 있습니다\n"
                        m += "'/{0} 지목 <번호>' 명령어로 지목할 수 있습니다".format(cmd)
                    else:
                        m += "현재 마피아가 제거할 인원을 지목하고 있습니다\n"
                        m += "날이 밝으면 결과가 공개됩니다. 당신이 아니길 바랍니다"

                sess.send_text(m, chat_id)

                m = "현재 생존자 목록\n"

                for i, player in zip(range(0, len(game.livings())), game.livings()):
                    m += "{0}. {1}\n".format(i, sess.get_user_nickname(chat_id, player))

                sess.send_text(m, chat_id)
        elif mode == 1:
            sub_cmd = args[0]

            if sub_cmd == "규칙":
                cmd = self.trigger()
                sess.send_text(MafiaGame.rule(cmd), chat_id)
        elif mode == 2:
            state = game.state()
            sub_cmd = args.pop(0)

            if sub_cmd == "지목":
                if author not in game.mafias():
                    sess.send_text("당신은 마피아가 아닙니다", chat_id)
                    return

                if chat_id not in game.mafia_rooms():
                    sess.send_text("마피아의 개인톡에서만 가능한 명령어입니다", chat_id)
                    return

                if state != game.STATE_NIGHT:
                    sess.send_text("밤이 올 때까지 기다려주세요", chat_id)
                    return

                try:
                    idx = int(args[0])

                    game.vote_by_mafia(author, idx, chat_id)
                    sess.send_text("지목했습니다", chat_id)
                except GameException as e:
                    sess.send_text(e.why(), chat_id)
                except:
                    sess.send_text("제거할 인원 번호가 올바르지 않습니다", chat_id)
