# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3

from lib.utils import format_time, get_function_arity_range

from lib.storage import (
    init_storage,
    close_storage,
    store_message,
    get_user_notes,
    delete_note,
    get_unread_news,
    mark_news_as_read
)

from lib.commands import parse_and_execute
from config.greetings import greetings

@irc3.plugin
class Plugin:
    def __init__(self, bot):
        init_storage()
        self.bot = bot

    @irc3.event(irc3.rfc.JOIN)
    def say_hi(self, mask, channel, **kw):
        """Say hi when someone join a channel"""
        if mask.nick != self.bot.nick:
            self.bot.privmsg(channel, 'Hi %s!' % mask.nick)
        else:
            self.bot.privmsg(channel, 'Hi!')

    @irc3.event(irc3.rfc.PRIVMSG)
    def handle_message(self, mask, target, data, **kw):
        irc = IRCMediator(self.bot, mask, target, data)
        if mask.nick != self.bot.nick and target != self.bot.nick:
            print("%s/%s: %s" % (irc.channel, irc.source, irc.msg))
            store_message(irc)
            parse_and_execute(irc)

class IRCMediator:
    def __init__(self, bot, mask, target, data):
        self.bot = bot
        self.mask = mask
        self.target = target
        self.data = data

    def send(self, target, message):
        if message == " " or message == " ":
            self.bot.privmsg(target, "\u00A0")
        else:
            self.bot.privmsg(target, message)

    @property
    def msg(self):
        return self.data

    @property
    def channel(self):
        return self.target

    @property
    def source(self):
        return self.mask.nick

