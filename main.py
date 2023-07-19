#!/usr/bin/env python

import irc.bot
import irc.strings
from random import randint
from lib.utils import format_time
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

class MyBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.nickname = nickname

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("[*] Server connection established.")
        c.join(self.channel)
        print("[*] Joined channel %s." % self.channel)

    def on_pubmsg(self, c, e):
        print("Event: ", e)
        store_message(e, self.channel)
        parse_and_execute(e, c)

    def on_join(self, c, e):
        greeting = greetings[randint(0, len(greetings) - 1)]
        if e.source.nick != self.nickname:
            c.privmsg(self.channel, greeting.replace("<username>", e.source.nick))
            self.communicate_notes(c, e)
            self.communicate_news(c, e)

    def communicate_notes(self, c, e):
        notes = get_user_notes(e.source.nick, self.channel)
        print("notes: %s", notes)

        if len(notes) > 0:
            c.privmsg(self.channel, "you have %d note/s %s." % (len(notes), e.source.nick))
        for note in notes:
            c.privmsg(self.channel, "> %s said: %s" % (note['source'], note['text']))
        for note in notes:
            delete_note(note['id'])

    def communicate_news(self, c, e):
        news = get_unread_news(e.source.nick, e.target)

        if len(news) > 0:
            c.privmsg(self.channel, "%s: There's news! (%s)" % (e.source.nick, len(news)))

        for item in news:
            time = format_time(item['timestamp'])
            c.privmsg(self.channel, "> [%s]: %s" % (time, item['text']))

        mark_news_as_read(e.source.nick, e.target, list(map(lambda n: n['id'], news)))

def main():
    try:
        init_storage()
        bot = MyBot("#wispers", "botboy", "irc.libera.chat")
        bot.start()
    except KeyboardInterrupt:
        print("[*] Exiting...")
    finally:
        close_storage()

if __name__ == "__main__":
    main()
