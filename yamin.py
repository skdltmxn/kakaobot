# -*- coding: utf-8 -*-

from bot.command import *

CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
JUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

lookup_table = {
    ("ㄷ", "ㅐ"): ("ㅁ", "ㅓ"),
    ("ㅁ", "ㅓ"): ("ㄷ", "ㅐ"),
    ("ㅁ", "ㅕ"): ("ㄸ", "ㅣ"),
    ("ㄸ", "ㅣ"): ("ㅁ", "ㅕ"),
    ("ㄷ", "ㅒ"): ("ㅁ", "ㅕ"),
    ("ㄱ", "ㅟ"): ("ㅋ", "ㅓ"),
    ("ㅍ", "ㅣ"): ("ㄱ", "ㅚ"),
    ("ㄱ", "ㅚ"): ("ㅍ", "ㅣ"),
    ("ㅍ", "ㅏ"): ("ㄱ", "ㅘ"),
    ("ㄱ", "ㅘ"): ("ㅍ", "ㅏ"),
    ("ㄱ", "ㅟ"): ("ㅋ", "ㅓ"),
    ("ㅋ", "ㅓ"): ("ㄱ", "ㅟ"),
    ("ㅇ", "ㅜ"): ("ㅇ", "ㅡ", "ㄱ"),
    ("ㅇ", "ㅡ", "ㄱ"): ("ㅇ", "ㅜ", ""),
    ("ㅇ", "ㅠ"): ("ㅇ", "ㅡ", "ㄲ"),
    ("ㅇ", "ㅡ", "ㄲ"): ("ㅇ", "ㅠ", ""),
    ("ㅇ", "ㅘ", "ㅇ"): ("ㅇ", "ㅏ", "ㅎ"),
    ("ㅇ", "ㅏ", "ㅎ"): ("ㅇ", "ㅘ", "ㅇ"),
    ("ㅎ", "ㅏ", "ㅎ"): ("ㅎ", "ㅘ", "ㅇ"),
    ("ㅎ", "ㅘ", "ㅇ"): ("ㅎ", "ㅏ", "ㅎ"),
    ("ㅌ", "ㅡ", "ㄵ"): ("ㅈ", "ㅏ", "ㅇ"),
    ("ㅅ", "ㅜ", "ㅍ"): ("ㄱ", "ㅣ", "ㅁ"),
    ("ㅇ", "ㅘ", ""): ("ㅎ", "ㅓ", ""),
    ("ㅎ", "ㅓ", ""): ("ㅇ", "ㅘ", ""),
    ("ㄸ", "ㅡ", ""): ("ㅂ", "ㅣ", ""),
    ("ㅂ", "ㅣ", ""): ("ㄸ", "ㅡ", ""),
    ("ㄸ", "ㅜ", ""): ("ㅂ", "ㅏ", ""),
    ("ㅂ", "ㅏ", ""): ("ㄸ", "ㅜ", ""),
    ("ㄸ", "ㅗ", ""): ("ㅂ", "ㅓ", ""),
    ("ㅂ", "ㅓ", ""): ("ㄸ", "ㅗ", ""),
    ("ㄸ", "ㅠ", ""): ("ㅂ", "ㅑ", ""),
    ("ㅂ", "ㅑ", ""): ("ㄸ", "ㅠ", ""),
    ("ㄸ", "ㅛ", ""): ("ㅂ", "ㅕ", ""),
    ("ㅂ", "ㅕ", ""): ("ㄸ", "ㅛ", "")
}

def decompose(letter):
    val = letter - 0xac00
    cho = val / 588
    jung = val / 28 % 21
    jong = val % 28

    return (CHO[cho], JUNG[jung], JONG[jong])

def compose((cho, jung, jong)):
    code = (CHO.index(cho) * 588) + (JUNG.index(jung) * 28) + JONG.index(jong)
    return unichr(0xac00 + code)

def convert(word):
    converted = ""

    for c in word:
        val = ord(c)

        if val < 0xac00 or val > 0xd7a3:
            converted += c
            continue

        han = decompose(val)

        sub = lookup_table.get(han[:2], ())
        if sub == ():
            sub = lookup_table.get(han, ())

        if sub != ():
            sub += han[len(sub):3]
            converted += compose(sub[:3])
        else:
            converted += c

    return converted


class YaminCommand(Command):
    def description(self):
        return "야민정음으로 번역한다"

    def usage(self):
        m = "'/{0} <문장>': <문장>을 야민정음올 번역한다\n\n".format(self.trigger())
        m += "주어진 <문장>을 야민정음으로 바꾼다\n"
        m += "<문장>이 이미 야민정음이면 정상 문장으로 다시 되돌린다\n"
        m += "ex) 대머리 -> 머대리, 댕댕이 -> 멍멍이"
        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()

        if len(args) < 1:
            sess.send_text(self.usage(), chat_id)
            return

        try:
            sentence = " ".join(args)
            converted = convert(sentence.decode("utf8"))
            sess.send_text(converted.encode("utf8"), chat_id)
        except:
            import traceback
            print traceback.format_exc()
