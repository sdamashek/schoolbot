import threading
import time
import irc.client
from twilio.rest import TwilioRestClient

class Notifier:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def notify(self, event):
        raise NotImplementedError

class IRCNotifier(Notifier):
    def __init__(self, network, nickname, channels, pings=None):
        self.events = []
        self.hostname, self.port = network
        self.nickname = nickname
        self.channels = channels
        self.reactor = None
        self.pings = pings
        threading.Thread(target=self.start, args=()).start()

    def start(self):
        self.reactor = irc.client.Reactor()
        self.connect()

    def connect(self):
        try:
            c = self.reactor.server().connect(self.hostname, self.port, self.nickname)
        except Exception as e:
            print "Connecting to IRC: " + str(e)
            time.sleep(5)
            threading.Thread(target=self.connect, args=()).start()
            return
        c.add_global_handler("welcome", self.on_connect)
        c.add_global_handler("disconnect", self.on_disconnect)

        self.reactor.process_forever()

    def on_connect(self, connection, event):
        print 'connected!'
        for channel in self.channels:
            connection.join(channel)
        threading.Thread(target=self.main_loop, args=(connection,)).start()

    def on_disconnect(self, connection, event):
        print "Error connecting, attempting to reconnect..."
        time.sleep(3)
        self.connect()

    def main_loop(self, connection):
        while True:
            for e in range(len(self.events)):
                print 'processing event %d' % e
                print self.events
                event = self.events[e]
                message = "FCPS will be %s on %s (%s)" % (event.title, event.date_text, event.description)
                if self.pings:
                    message = ','.join(self.pings) + ': ' + message
                for channel in self.channels:
                    connection.privmsg(channel, message)
            self.events = []

    def notify(self, event):
        self.events.append(event)

class WindowsNotifier(Notifier):
    def __init__(self):
        pass

    def _notify(self, event):
        import ctypes
        import winsound
        winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
        ctypes.windll.user32.MessageBoxW(0, "FCPS will be %s on %s (%s)" % (event.title, event.date_text, event.description), "Update", 0)

    def notify(self, event):
        threading.Thread(target=self._notify, args=(event,)).start()

class TextNotifier(Notifier):
    def __init__(self, users):
        self.users = users

    def _notify(self, event):
        from config import ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER
        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

        for user in self.users:
            message = client.messages.create(
                body = "FCPS will be %s on %s (%s) -- fcpsbot" % (event.title, event.date_text, event.description),
                to=user,
                from_=TWILIO_NUMBER
            )
            print message.sid

    def notify(self, event):
        threading.Thread(target=self._notify, args=(event,)).start()