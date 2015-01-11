from notifier import *
from source import *
import os
import datetime

if __name__ == '__main__':
    sources = [FCPSSource(), TwitterSource("fcpsnews", r'all +schools.+will +(.+)on +(.+)'), TwitterSource("RyanLMcElveen", r'FCPS.*will(.+)(?:on|tomorrow|today)(.+)')]
    notifiers = [IRCNotifier(("chat.freenode.net",6667), "fcpsbot", ["#fcpsbot", "#tjhsst"], ["sdamashek", "jwoglom", "fwilson"]), TextNotifier(["+15713582032"])]

    if os.name == 'nt':
        notifiers.append(WindowsNotifier())

    for source in sources:
        source.poll()

    while True:
        for source in sources:
            if source.event != source.old_event:
                source.old_event = source.event
                delta = source.event.date - datetime.datetime.today()
                if delta.days >= 0:
                    for n in notifiers:
                        n.notify(source.event)