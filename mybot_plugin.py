# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3

from random import randint
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
        irc = IRCMediator(self.bot, mask, channel)
        greeting = greetings[randint(0, len(greetings) - 1)]
        if mask.nick != self.bot.nick:
            irc.send(irc.channel, greeting.replace("<username>", irc.source))
            communicate_notes(irc)
            communicate_news(irc)

    @irc3.event(irc3.rfc.PRIVMSG)
    def handle_message(self, mask, target, data, **kw):
        irc = IRCMediator(self.bot, mask, target, data)
        if mask.nick != self.bot.nick and target != self.bot.nick:
            print("%s/%s: %s" % (irc.channel, irc.source, irc.msg))
            store_message(irc)
            parse_and_execute(irc)

def communicate_notes(irc):
    notes = get_user_notes(irc.source,  irc.channel)
    print("notes: %s", notes)

    if len(notes) > 0:
        irc.send(irc.channel, "you have %d note/s %s." % (len(notes), irc.source))
    for note in notes:
        irc.send(irc.channel, "> %s said: %s" % (note['source'], note['text']))
    for note in notes:
        delete_note(note['id'])

def communicate_news(irc):
    news = get_unread_news(irc.source, irc.channel)

    if len(news) > 0:
        irc.send(irc.channel, "%s: There's news! (%s)" % (irc.source, len(news)))

    for item in news:
        time = format_time(item['timestamp'])
        irc.send(irc.channel, "> [%s]: %s" % (time, item['text']))

    mark_news_as_read(irc.source, irc.channel, list(map(lambda n: n['id'], news)))

class IRCMediator:
    def __init__(self, bot, mask, target, data = None):
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

