# -*- coding: utf-8 -*-

from bot.command import *


class HelpCommand(Command):
    def __init__(self, trigger, commands):
        super(HelpCommand, self).__init__(trigger)
        self._commands = commands
        
    def description(self):
        return "사용 가능한 명령어 목록을 출력한다"
        
    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 사용 가능한 명령어 목록을 출력한다\n".format(cmd)
        m += "'/{0} <명령어>': 명령어의 자세한 사용법을 출력한다\n\n".format(cmd)
        m += "<명령어>에는 '/'를 제외한 값을 입력한다\n"
        m += "ex) '/{0} {0}': '{0}' 명령어의 자세한 사용법을 출력".format(cmd)
        return m
        
    def run(self, sess, args, chat):
        chat_id = chat.chat_id()
        
        if len(args) == 0:
            msg = "명령어 목록\n"
            
            for trigger, command in self._commands.iteritems():
                msg += "/{0}: {1}\n".format(trigger, command.description())
            
            sess.send_text(msg.strip(), chat_id)
        else:
            cmd = args.pop(0)
            command = self._commands.get(cmd)
            
            if command is None:
                sess.send_text("'{0}' 존재하지 않는 명령어입니다".format(cmd), chat_id)
            else:
                sess.send_text(command.usage(), chat_id)
