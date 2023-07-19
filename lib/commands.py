import shlex
import inspect
from datetime import datetime

from lib.storage import get_messages, store_note, store_news, get_unread_news, get_news
from lib.utils import format_time, get_function_arity_range

command_info = {}
command_handlers = {}

def parse_and_execute(event, irc):
    words = shlex.split(event.arguments[0])
    if words[0] == '@boy' or words[0] == '@botboy':
        handle_command(words[1], words[2:], event, irc)

def handle_command(command, args, event, irc):
    # print("Executing command %s with args %s" % (command, args))

    if command in command_handlers:
        arity_range = get_function_arity_range(command_handlers[command])
        arg_range = [arity_range[0] -2, arity_range[1] -2]
        if len(args) < arg_range[0] or len(args) > arg_range[1]:
            range_str = "%s-%s" % (arg_range[0], arg_range[1])
            error_str = "Error: Invalid number of arguments. Expected %s" % range_str
            irc.privmsg(event.source.nick, error_str)
            display_command_help(event, irc, command)
        else:
            command_handlers[command](event, irc, *args)
    else:
        irc.privmsg(event.source.nick, "Error: Unknown command.")


# Command decorator

def register_command(func):
    """A decorator to register function metadata in a global dictionary."""
    command_info[func.__name__] = func.__doc__
    command_handlers[func.__name__] = func
    return func

# Commands

@register_command
def history(event, irc, limit=5):
    """
    Prints the last <limit> messages.

    Example: @boy history 5

    Parameters:
        limit: The number of messages to print. (default: 5, max: 10)
    """
    messages = get_messages(event.target, limit)[:10]
    irc.privmsg(event.source.nick, " ")
    for message in messages:
        time = format_time(message['timestamp'])
        irc.privmsg(event.source.nick, "[%s] %s: %s" % (time, message['user'], message['message']))

@register_command
def note(event, irc, user, text):
    """
    Sends a note to a user. They will receive it the next time they join the channel.

    Example: @boy note <user> "Remember to do the thing!"

    Parameters:
        user: The user to send the note to.
        text: The text of the note.
    """
    store_note(event.source.nick, user, text, event.target)
    irc.privmsg(event.target, "Note stored successfully for %s." % user)

@register_command
def publish_news(event, irc, text, expires=10):
    """
    Publishes news to the channel. They will be shown to users who join the channel.

    Example: @boy publish_news "Remember to do the thing!" 30

    Parameters:
        text: The text of the news.
        expires: The number of days the news will be shown to users. (default: 10)
    """
    store_news(event.source.nick, text, event.target, expires)
    irc.privmsg(event.target, "News were registered.")

@register_command
def news(event, irc):
    """
    Shows the news for the channel.

    Example: @boy news
    """
    irc.privmsg(event.source.nick, " ")
    news = get_news(event.target)
    if len(news) > 0:
        irc.privmsg(event.source.nick, "Showing news:")
    for item in news:
        time = format_time(item['timestamp'])
        irc.privmsg(event.source.nick, "> [%s]: %s" % (time, item['text']))

# @register_command
# def unread_news(event, irc):
#     news = get_unread_news(event.source.nick, event.target)
#     for item in news:
#         time = format_time(item['timestamp'])
#         irc.privmsg(event.source.nick, "[%s]: %s" % (time, item['text']))

@register_command
def help(event, irc, command=None):
    """
    Prints help for a command.

    Example: @boy help history

    Parameters:
        command: The command to print help for.
    """
    if command:
        return display_command_help(event, irc, command)

    irc.privmsg(event.source.nick, " ")
    commands = list(command_info.keys())
    irc.privmsg(event.source.nick, "Select a command you'd like help with.")
    irc.privmsg(event.source.nick, "> @boy help <command>")
    irc.privmsg(event.source.nick, " ")
    irc.privmsg(event.source.nick, "Available commands:")
    for command in commands:
        irc.privmsg(event.source.nick, "- %s" % command)

# Utils

def display_command_help(event, irc, command):
    irc.privmsg(event.source.nick, " ")
    if command in command_info:
        irc.privmsg(event.source.nick, "Help for command %s:" % command)
        lines = command_info[command].split("\n")
        for line in lines:
            irc.privmsg(event.source.nick, line + " ") # make empty strings visible
    else:
        irc.privmsg(event.source.nick, "Command %s does not exist." % command)
    return
