# -*- coding: utf-8 -*-

from models.locologinlistrequest import *
from models.locobuyticketrequest import *
from models.locobuyticketresponse import *
from models.locochatinforequest import *
from models.locochatonroomrequest import *
from models.lococreaterequest import *
from models.lococreateresponse import *
from models.locogetmemrequest import *
from models.locogetmemresponse import *
from models.locomchatlogsrequest import *
from models.locomchatlogsresponse import *
from models.locomemberrequest import *
from models.locomemberresponse import *
from models.locomessageresponse import *
from models.locopingrequest import *
from models.locopingresponse import *
from models.locowriterequest import *
from models.locoagent import *
import json
import threading
import gevent
from gevent.event import Event


class Session(object):
    def __init__(self, wc, user_id, account_id, session_key, duuid):
        self._wc = wc
        self._user_id = user_id
        self._account_id = account_id
        self._session_key = session_key
        self._duuid = duuid
        self._ticket_agent = LocoAgent()
        self._ticket_agent.connect("110.76.142.19", 5223)
        self._carriage_agent = LocoAgent()
        self._carriage_agent.set_packet_handler_method("MSG", self.on_read_msg)
        self._carriage_agent.set_packet_handler_method("DECUNREAD", self.ignore)
        self._carriage_agent.set_packet_handler_method("WRITE", self.ignore)
        self._carriage_agent.set_packet_handler_method("INVOICE", self.ignore)
        self._bot = None
        self._ping_timer = None
        self._user_id_map = {}
        self._active = False
        self._run_event = Event()

    def run(self):
        ticket = self.buy_ticket()
        self._ticket_agent.close()
        self._carriage_agent.connect(ticket.host(), ticket.port())
        self.send_login_list()
        self._ping_timer = gevent.spawn(self.send_ping)
        self._active = True

        if self._bot is not None:
            self._bot.on_connect(self)

    def close(self):
        if not self._active:
            return

        try:
            self._bot.on_shutdown(self)
            self._bot.shutdown()

            if self._ping_timer is not None:
                self._ping_timer.kill()
                self._ping_timer.join()

            self._ticket_agent.close()
            self._carriage_agent.close()
        except:
            import traceback
            print "---- session.close ----"
            print traceback.format_exc()
            print "-----------------------"
        finally:
            self._active = False

    def set_run_event(self):
        self._run_event.set()

    def join(self):
        self._run_event.wait()

    def ignore(self, _):
        pass

    def register_bot(self, bot):
        self._bot = bot

    def on_read_msg(self, response):
        msg = LocoMessageResponse(response)
        if msg.error() != "":
            print msg.error()
            return

        try:
            if self._bot is not None:
                self._bot.on_msg(self, msg)
        except:
            import traceback
            print "----- on_read_msg error -----"
            print traceback.format_exc()
            print "-----------------------------"

    def buy_ticket(self):
        req = LocoBuyTicketRequest(
            userId=long(self._user_id),
            appVer="2.2.4",
            os="mac",
            ntype=0,
            MCCMNC="999",
            countryISO="KR",
            voip=True,
            useSub=True
        )

        ret = self._ticket_agent.send_request(req)
        return LocoBuyTicketResponse(ret)

    def send_login_list(self):
        req = LocoLoginListRequest(
            lang = "ko",
            ntype = 0,
            rp = None,
            dtype = 2,
            lastTokenId = long(0),
            pcst = 1,
            MCCMNC = "999",
            appVer = "2.2.4",
            bg = False,
            oauthToken = None,
            maxIds = [],
            duuid = self._duuid,
            sKey = self._session_key,
            lbk = 0,
            chatIds = [],
            os = "mac",
            revision = 0
        )

        return self._carriage_agent.send_request(req)

    def send_chat_info(self, chat_id):
        req = LocoChatInfoRequest(
            chatId = chat_id
        )

        return self._carriage_agent.send_request(req)

    def send_text(self, msg, chat_id):
        return self.send_write(msg, chat_id, 1)

    def send_picture(self, msg, chat_id, **picture):
        return self.send_write(msg, chat_id, 2, picture)

    def send_emoticon(self, msg, chat_id, type, **emoticon):
        return self.send_write(msg, chat_id, type, emoticon)

    def send_write(self, msg, chat_id, type, extra=None):
        if extra is None:
            extra = ""
        else:
            extra = json.dumps(extra)

        req = LocoWriteRequest(
            chatId = chat_id,
            msgId = long(0),
            msg = msg.decode("utf8"),
            type = type,
            noSeen = False,
            extra = extra
        )

        return self._carriage_agent.send_request(req)

    def send_mchat_logs(self, chat_id, since):
        req = LocoMChatLogsRequest(
            chatIds = [long(chat_id)],
            sinces = [long(since)]
        )

        result = self._carriage_agent.send_request(req)
        return LocoMChatLogsResponse(result)

    def send_chat_on_room(self, chat_id):
        req = LocoChatOnRoomRequest(
            chatId = chat_id,
            token = long(0),
            opt = 0
        )

        ret = self._carriage_agent.send_request(req)

        for member in ret["m"]:
            self._user_id_map[member["userId"]] = member["nickName"].encode("utf8")

        return ret

    def send_ping(self):
        while True:
            gevent.sleep(60.0)
            pong = self.send_ping_request()
            pong = LocoPingResponse(pong)
            if pong.error() != "":
                print "[-] Ping error: {0}".format(pong.errMsg())

    def send_ping_request(self):
        req = LocoPingRequest()
        return self._carriage_agent.send_request(req)

    def send_member_info(self, chat_id, *member_ids):
        req = LocoMemberRequest(
            chatId = long(chat_id),
            memberIds = map(long, member_ids)
        )

        ret = self._carriage_agent.send_request(req)
        ret = LocoMemberResponse(ret)

        for member in ret.members():
            self._user_id_map[member.user_id()] = member.nickname()

        return ret

    def send_create(self, *member_ids):
        req = LocoCreateRequest(
            pushAlert = False,
            memoChat = False,
            memberIds = map(long, member_ids)
        )

        ret = self._carriage_agent.send_request(req)
        return LocoCreateResponse(ret)

    def send_get_mem(self, chat_id):
        req = LocoGetMemRequest(
            chatId = long(chat_id)
        )

        ret = self._carriage_agent.send_request(req)
        ret = LocoGetMemResponse(ret)

        for member in ret.members():
            self._user_id_map[member.user_id()] = member.nickname()

        return ret

    def get_user_nickname(self, chat_id, member_id):
        nickname = self._user_id_map.get(member_id) or ""

        if nickname == "":
            member = self.send_member_info(chat_id, member_id)
            member = LocoMemberResponse(member)

            if member.status() != 0 or len(member.members()) == 0:
                raise ValueError("Non existent member_id!")

            nickname = member.members()[0].nickname()
            self._user_id_map[member_id] = nickname

        return nickname

    def my_user_id(self):
        return self._user_id
