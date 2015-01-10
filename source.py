import threading
import requests
import time
import re
import dateutil.parser as dparser
import datetime
import tweepy

from event import Event

class Source:

    def __init__(self, *args, **kwargs):
        self.event = None
        self.old_event = None

    def _poll(self):
        raise NotImplementedError()

    def poll(self):
        threading.Thread(target=self._poll, args=()).start()

class TwitterSource(Source):

    def __init__(self, user, regex):
        self.user = user
        self.regex = regex
        self.event = None
        self.old_event = None

    def _poll(self):
        from config import consumer_key, consumer_secret, access_token, access_secret
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        api = tweepy.API(auth)

        while True:
            tweets = api.user_timeline(self.user)
            for tweet in tweets:
                match = re.search(self.regex, tweet.text, re.IGNORECASE)
                if match and len(match.groups()) == 2:
                    print match.groups()
                    tstr, dstr = match.groups()

                    if 'two hour' in tstr.lower() or '2 hour' in tstr.lower():
                        t = Event.DELAY
                    else:
                        t = Event.CLOSING

                    try:
                        d = dparser.parse(dstr, fuzzy=True)
                    except ValueError:
                        d = datetime.datetime.today() + datetime.timedelta(days=1)

                    title = 'delayed by two hours' if t == Event.DELAY else 'closed'
                    desc = '"%s" -- @%s' % (tweet.text, self.user)
                    self.event = Event(t, title, desc, d)
                    break
            time.sleep(30)



class FCPSSource(Source):
    def _poll(self):
        while True:
            page = requests.get('http://www.fcps.edu/news/emerg.shtml').text
            #page = """<p><strong>Thursday, January 8 - 5 p.m. </strong></p>
#<h3 id="c3">All  Fairfax County public schools and offices will open two hours late on Monday, January 12 (Condition 3). Central  offices will open at 10 a.m. </h3>
#<ul>"""
            for line in page.split('\n'):
                match = re.search(r'all +fairfax +county +public +schools +(.*) +on +(.*)', line, re.IGNORECASE)
                if match and len(match.groups()) == 2:
                    tstr, dstr = match.groups()

                    if 'two hour' in tstr.lower() or '2 hour' in tstr.lower():
                        t = Event.DELAY
                    else:
                        t = Event.CLOSING

                    try:
                        d = dparser.parse(dstr, fuzzy=True)
                    except ValueError:
                        d = datetime.datetime.today() + datetime.timedelta(days=1)

                    title = 'delayed by two hours' if t == Event.DELAY else 'closed'
                    desc = '"%s" -- fcps.edu' % line
                    self.event = Event(t, title, desc, d)
                    break

            time.sleep(5)