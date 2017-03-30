# -*- coding: utf-8 -*-

from bot.command import *
from util.webclient import WebClient
from urllib import unquote


wc = WebClient("https://app.genie.co.kr/Iv3")
wc.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0")


class MusicSearchCommand(Command):
    def description(self):
        return "음악을 검색한다"

    def usage(self):
        m = "'/{0} <키워드>': <키워드>로 음악을 검색한다\n\n".format(self.trigger())
        m += "주어진 <키워드>가 포함된 음악을 검색한다\n"
        m += "결과는 최대 5개까지 출력되며 <키워드>는 공백을 포함할 수 있다"
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()

        if len(args) < 1:
            sess.send_text(self.usage(), chat_id)
            return

        query = " ".join(args)
        try:
            result = wc.get("/Search/f_Search_Song.asp",
                page=1,
                pagesize=5,
                hl="false",
                fscount="true",
                order="false",
                of="score",
                query=query)

            msg = result["result"]["message"]
            exist = result["result"]["exist"]
            if msg is not None:
                sess.send_text(msg.encode("utf8"), chat_id)

            if not exist:
                sess.send_text("검색 결과가 없습니다", chat_id)
                return

            msg = "검색 결과\n"
            songs = result["items"]["song"]
            for song in songs["items"]:
                msg += "{0} {1} - {2}\n".format(
                    song["SONG_ID"].encode("utf8"),
                    song["SONG_NAME"].encode("utf8"),
                    song["ARTIST_NAME"].encode("utf8")
                )

            sess.send_text(msg.rstrip(), chat_id)

        except:
            import traceback
            print traceback.format_exc()
            sess.send_text("검색 에러", chat_id)


class MusicDownloadCommand(Command):
    def description(self):
        return "음악을 다운로드한다"

    def usage(self):
        m = "'/{0} <음악ID>': <음악ID>에 해당하는 음악을 다운로드한다\n\n".format(self.trigger())
        m += "<음악ID>는 음악 검색 명령어를 통해 확인할 수 있다"
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()

        if len(args) < 1:
            sess.send_text(self.usage(), chat_id)
            return

        try:
            result = wc.get("/Member/Login/j_Member_Login.asp",
                uxtk="",
                isi="11353535951",
                dcd="12:34:56:78:9a:bc")

            login_data = result["DATA0"]
            song_id = args[0]
            result = wc.get("/Player/j_appStmInfo.asp",
                xgnm=song_id,
                bitrate="320",
                isi="11353535951",
                unm=login_data["MemUno"].encode("utf8"),
                uxtk=login_data["MemToken"].encode("utf8"))

            if result["Result"]["RetCode"] != "0":
                raise

            data = result["DataSet"]["DATA"]
            if len(data) == 0:
                raise

            data = data[0]
            song_name = unquote(data["SONG_NAME"]).encode("utf8")
            artist = unquote(data["ARTIST_NAME"]).encode("utf8")
            duration = int(data["SONG_DURATION"])
            msg = "{0} - {1}\n".format(song_name, artist)
            msg += "길이: {0}분 {1}초\n".format(duration / 60, duration % 60)
            msg += "링크: {0}".format(unquote(data["STREAMING_MP3_URL"]))
            sess.send_text(msg, chat_id)
        except:
            import traceback
            print traceback.format_exc()
            sess.send_text("<음악ID>에 해당하는 음악이 없습니다", chat_id)
