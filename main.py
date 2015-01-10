from notifier import *
from source import *

sources = [FCPSSource(), TwitterSource("fcpsnews", r'all +schools.+will +(.+)on +(.+)'), TwitterSource("RyanLMcElveen", r'FCPS.*will(.+)(?:on|tomorrow|today)(.+)')]
notifiers = [IRCNotifier(("chat.freenode.net",6667), "fcpsbot", ["#fcpsbot"])]

for source in sources:
    source.poll()

#event = Event(Event.DELAY, "delayed by two hours", "ayy lmao", "January 10th, 2015")

while True:
    for source in sources:
        if source.event != source.old_event:
            source.old_event = source.event
            for n in notifiers:
                n.notify(source.event)