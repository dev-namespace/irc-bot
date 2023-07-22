import shlex
import inspect
from datetime import datetime

from lib.storage import get_messages, store_note, store_news, get_unread_news, get_news
from lib.utils import format_time, get_function_arity_range

command_info = {}
command_handlers = {}

def parse_and_execute(irc):
    # if words[0] == '@boy' or words[0] == '@botboy':
    if irc.msg[0] == "!":
        words = shlex.split(irc.msg[1:])
        handle_command(words[0], words[1:], irc)

def handle_command(command, args, irc):
    # print("Executing command %s with args %s" % (command, args))

    if command in command_handlers:
        arity_range = get_function_arity_range(command_handlers[command])
        arg_range = [arity_range[0] -1, arity_range[1] -1]
        if len(args) < arg_range[0] or len(args) > arg_range[1]:
            range_str = "%s-%s" % (arg_range[0], arg_range[1])
            error_str = "Error: Invalid number of arguments. Expected %s" % range_str
            irc.send(irc.channel, error_str)
            display_command_help(irc, command)
        else:
            command_handlers[command](irc, *args)
    else:
        irc.send(irc.channel, "Error: Unknown command.")


# Command decorator

def register_command(func):
    """A decorator to register function metadata in a global dictionary."""
    command_info[func.__name__] = func.__doc__
    command_handlers[func.__name__] = func
    return func

# Commands

@register_command
def history(irc, limit=5):
    """
    Prints the last <limit> messages.

    Example: !history 5

    Parameters:
        limit: The number of messages to print. (default: 5, max: 10)
    """
    messages = get_messages(irc.channel, limit)[:10]
    irc.send(irc.source, " ")
    for message in messages:
        time = format_time(message['timestamp'])
        irc.send(irc.source, "[%s] %s: %s" % (time, message['user'], message['message']))

@register_command
def note(irc, user, text):
    """
    Sends a note to a user. They will receive it the next time they join the channel.

    Example: !note <user> "Remember to do the thing!"

    Parameters:
        user: The user to send the note to.
        text: The text of the note.
    """
    store_note(irc.source, user, text, irc.channel)
    irc.send(irc.channel, "Note stored successfully for %s." % user)

@register_command
def publish_news(irc, text, expires=10):
    """
    Publishes news to the channel. They will be shown to users who join the channel.

    Example: !publish_news "Remember to do the thing!" 30

    Parameters:
        text: The text of the news.
        expires: The number of days the news will be shown to users. (default: 10)
    """
    store_news(irc.source, text, irc.channel, expires)
    irc.send(irc.channel, "News were registered.")

@register_command
def news(irc):
    """
    Shows the news for the channel.

    Example: !news
    """
    irc.send(irc.source, " ")
    news = get_news(irc.channel)
    if len(news) > 0:
        irc.send(irc.source, "Showing news:")
    for item in news:
        time = format_time(item['timestamp'])
        irc.send(irc.source, "> [%s]: %s" % (time, item['text']))

# # @register_command
# # def unread_news(event, irc):
# #     news = get_unread_news(event.source.nick, event.target)
# #     for item in news:
# #         time = format_time(item['timestamp'])
# #         irc.privmsg(event.source.nick, "[%s]: %s" % (time, item['text']))

@register_command
def help(irc, command=None):
    """
    Prints help for a command.

    Example: !help history

    Parameters:
        command: The command to print help for.
    """
    if command:
        return display_command_help(irc, command)

    irc.send(irc.source, " ")
    commands = list(command_info.keys())
    irc.send(irc.source, "Select a command you'd like help with.")
    irc.send(irc.source, "> !help <command>")
    irc.send(irc.source, " ")
    irc.send(irc.source, "Available commands:")
    for command in commands:
        irc.send(irc.source, "- %s" % command)

# Utils

def display_command_help(irc, command):
    irc.send(irc.source, " ")
    if command in command_info:
        irc.send(irc.source, "Help for command %s:" % command)
        lines = command_info[command].split("\n")
        for line in lines:
            irc.send(irc.source, line + " ") # make empty strings visible
    else:
        irc.send(irc.source, "Command %s does not exist." % command)
    return
