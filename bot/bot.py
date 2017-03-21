# -*- coding: utf-8 -*-

from models.locomessageresponse import *


class Bot(object):
    def __init__(self):
        self._commands = {}
        
    def shutdown(self):
        pass
    
    def on_connect(self, sess):
        pass
    
    def on_msg(self, *args, **kwargs):
        pass
    
    def on_shutdown(self, sess):
        pass
     
    def _process_global_command(self, sess, token, chat):
        # execute command for globel chatroom
        cmd = self._commands.get(0)
        if cmd is None:
            return

        trigger = token.pop(0)

        cmd = cmd.get(trigger)
        if cmd is None:
            return
        
        cmd.run(sess, token, chat)
       
    def process_command(self, sess, msg):
        chat = msg.chat_log()
        message = chat.message()
        chat_id = msg.chat_id()
        
        if message.startswith("/"):
            # run command for given chatroom
            token = message[1:].split()
            cmd = self._commands.get(chat_id)
            
            if cmd is None:
                self._process_global_command(sess, token, chat)
                return
            
            trigger = token.pop(0)
            
            cmd = cmd.get(trigger)
            if cmd is None:
                return
                
            cmd.run(sess, token, chat)
    
    def add_command(self, target, command):
        cmd = self._commands.get(target) or {}
        cmd[command.trigger()] = command
        self._commands[target] = cmd
