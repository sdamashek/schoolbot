import threading
import irc.client
import time

class Notifier:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def notify(self, event):
        raise NotImplementedError

class IRCNotifier(Notifier):
    def __init__(self, network, nickname, channels):
        self.events = []
        self.hostname, self.port = network
        self.nickname = nickname
        self.channels = channels
        self.reactor = None
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
                message = "FCPS will be %s on %s (%s)" % (event.title, event.date, event.description)
                for channel in self.channels:
                    connection.privmsg(channel, message)
            self.events = []

    def notify(self, event):
        self.events.append(event)
