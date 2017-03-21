# -*- coding: utf-8 -*-

from bot.command import *
import json


class Variable(object):
    def __init__(self, *args, **kwargs):
        self._var = {}

    @staticmethod
    def load(cur):
        var = Variable()
        try:
            cur.execute("SELECT data FROM pickled WHERE type = 'variable';")
            unicode_var = json.loads(cur.fetchone()[0])
            utf8_var = {}

            for k, v in unicode_var.iteritems():
                utf8_var[k.encode("utf8")] = [x.encode("utf8") for x in v]

            var._var = utf8_var
        except:
            import traceback
            print "---- Variable.load ----"
            print traceback.format_exc()
            print "-----------------------"

        return var

    @staticmethod
    def save(cur, var):
        try:
            data = json.dumps(var)
            cur.execute("SELECT count(data) FROM pickled WHERE type = 'variable';")

            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO pickled (type, data) VALUES (%s, %s);", ("variable", data))
            else:
                cur.execute("UPDATE pickled SET data=(%s) WHERE type=(%s);", (data, "variable"))
        except:
            import traceback
            print "---- Variable.save ----"
            print traceback.format_exc()
            print "-----------------------"

    def get_var(self, var):
        return self._var.get(var)

    def append(self, var, val):
        if var in self._var:
            self._var[var].append(val)
        else:
            self._var[var] = [val]

    def remove(self, var, idx):
        self._var[var].pop(idx)
        if len(self._var[var]) == 0:
            del self._var[var]

    def remove_all(self, var):
        del self._var[var]

    def var(self):
        return self._var


class VariableListOrAddCommand(Command):
    def __init__(self, trigger, var):
        super(VariableListOrAddCommand, self).__init__(trigger)
        self._var = var

    def description(self):
        return "기억을 확인하거나 추가한다"

    def usage(self):
        cmd = self.trigger()
        msg = "'/{0}': 전체 기억 목록을 출력한다\n".format(cmd)
        msg += "'/{0} <기억>': 특정 기억을 출력한다\n".format(cmd)
        msg += "'/{0} <기억> <값>': <기억>에 <값>을 저장한다\n\n".format(cmd)
        msg += "<기억>은 공백없는 문자열이며 <값>에은 임의의 문자열을 사용할 수 있습니다"
        return msg

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()
        variable = self._var.var()

        mode = len(args)
        if mode == 0:
            m = "[기억 목록]\n"
            for k, v in variable.iteritems():
                m += "{0} = {1}\n".format(k, ", ".join(v))

            m = m[:-1]
            sess.send_text(m, chat_id)
        elif mode == 1:
            var = args[0]
            var = var.replace("\t\r\n", "")
            var_list = self._var.get_var(var)

            if var_list is not None:
                sess.send_text("{0} = {1}".format(var, ", ".join(var_list)), chat_id)
            else:
                sess.send_text("'{0}' 없는 기억".format(var), chat_id)
        else:
            var = args.pop(0)
            val = " ".join(args)

            self._var.append(var, val)
            sess.send_text("기억 추가됨".format(var, val), chat_id)


class VariableRemoveSingleCommand(Command):
    def __init__(self, trigger, var):
        super(VariableRemoveSingleCommand, self).__init__(trigger)
        self._var = var

    def description(self):
        return "기억 하나를 제거한다"

    def usage(self):
        cmd = self.trigger()
        msg = "'/{0} <기억> <인덱스>': 기억 하나를 삭제한다\n\n".format(cmd)
        msg += "<기억>의 리스트 중 <인덱스>번째 값을 삭제합니다.\n"
        msg += "<인덱스>는 0부터 시작하며 <기억>의 길이값을 초과할 수 없습니다"
        return msg

    def run(self, sess, args, chat):
        cmd = self.trigger()
        chat_id = chat.chat_id()

        try:
            var = args[0]
            idx = int(args[1])
            var_list = self._var.get_var(var)

            if var_list is not None:
                if idx < 0 or idx >= len(var_list):
                    sess.send_text("인덱스 오류", chat_id)
                    return

                self._var.remove(var, idx)

                sess.send_text("'{0}' 삭제 완료".format(var), chat_id)
            else:
                sess.send_text("'{0}' 없는 기억".format(var), chat_id)
        except:
            sess.send_text(self.usage(), chat_id)


class VariableRemoveAllCommand(Command):
    def __init__(self, trigger, var):
        super(VariableRemoveAllCommand, self).__init__(trigger)
        self._var = var

    def description(self):
        return "기억 하나를 전부 제거한다"

    def usage(self):
        cmd = self.trigger()
        msg = "'/{0} <기억>': 기억을 삭제한다\n\n".format(cmd)
        msg += "<기억>에 저장된 모든 값을 삭제합니다."
        return msg

    def run(self, sess, args, chat):
        cmd = self.trigger()
        chat_id = chat.chat_id()

        if len(args) < 1:
            sess.send_text(self.usage(), chat_id)
            return

        var = args[0]

        if self._var.get_var(var) is not None:
            self._var.remove_all(var)
            sess.send_text("{0} 전체 삭제 완료".format(var), chat_id)
        else:
            sess.send_text("'{0}' 없는 기억".format(var), chat_id)
