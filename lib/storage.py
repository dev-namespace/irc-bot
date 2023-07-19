import sqlite3
import datetime
import shelve
import uuid

from lib.date import get_cest_datetime

conn = None
store = None

def init_storage():
    global conn, store
    conn = sqlite3.connect('mydatabase.db')
    store = shelve.open('store')

    # store['%s/news' % "#wispers-test"] = []

    # remove expired news for #wispers-test
    news = store.get('%s/news' % "#wispers", [])
    news = list(filter(lambda n: n['timestamp'] > get_cest_datetime() - datetime.timedelta(days=n["expiry_days"]), news))
    store['%s/news' % "#wispers"] = news

    with conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS Messages
            (id INTEGER PRIMARY KEY, message TEXT, channel TEXT, user TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS Notes
            (id INTEGER PRIMARY KEY, text TEXT, channel TEXT, source TEXT, target TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')

        print("[*] Storage initialized.")

def close_storage():
    global conn, store
    conn.close()
    store.close()
    conn = None
    store = None
    print("[*] Storage closed gracefully.")

def store_message(event, channel):
    date = get_cest_datetime()

    with conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO Messages (message, channel, user, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (event.arguments[0], channel, event.source.nick, date))

def get_messages(channel, limit = 100):
    with conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM Messages WHERE channel = ? ORDER BY timestamp DESC LIMIT ?
        ''', (channel, limit))
        rows = c.fetchall()
        return list(map(lambda row: {
            'id': row[0],
            'message': row[1],
            'channel': row[2],
            'user': row[3],
            'timestamp': row[4]
        }, reversed(rows)))

# Notes

def store_note(source, target, text, channel):

    with conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO Notes (source, target, text, channel, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (source, target, text, channel, get_cest_datetime()))

def get_user_notes(user, channel):
    with conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM Notes WHERE target = ? AND channel = ? ORDER BY timestamp DESC
        ''', (user, channel))
        rows = c.fetchall()
        return list(map(lambda row: {
            'id': row[0],
            'text': row[1],
            'channel': row[2],
            'source': row[3],
            'target': row[4],
            'timestamp': row[5]
        }, reversed(rows)))

def delete_note(note_id):
    with conn:
        c = conn.cursor()
        c.execute('''
            DELETE FROM Notes WHERE id = ?
        ''', (note_id,))


# News

def store_news(source, text, channel, expiry_days=10):
    news = store.get('%s/news' % channel, [])
    news.append({
        'id': uuid.uuid4(),
        'source': source,
        'text': text,
        'channel': channel,
        'expiry_days': expiry_days,
        'read_by': [],
        'timestamp': get_cest_datetime()
    })
    store['%s/news' % channel] = news


def get_news(channel, filter_expired = True):
    news = store.get('%s/news' % channel, [])
    return list(filter(lambda n: n['timestamp'] >= get_cest_datetime() - datetime.timedelta(days=n["expiry_days"]), news))

def get_unread_news(user, channel, filter_expired = True):
    news = get_news(channel, filter_expired)
    unread =  list(filter(lambda n: user not in n['read_by'], news))
    return unread

# @TODO optimize
def mark_news_as_read(user, channel, news_ids):
    news = store.get('%s/news' % channel, [])
    for n in news:
        if n['id'] in news_ids:
            n['read_by'].append(user)
    store['%s/news' % channel] = news
