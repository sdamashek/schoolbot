class Event:
    DELAY = 1
    CLOSING = 2

    def __init__(self, t, title, description, date):
        self.t = t
        self.title = title
        self.description = description
        self.date = date
        self.date_text = self.date.strftime('%A, %B %d')

    def __eq__(self, other):
        return self.description == other.description and self.date == other.date and self.t == other.t and self.title == other.title

    def __ne__(self, other):
        if type(other) != type(self):
            return True
        return self.description != other.description or self.date != other.date or self.t != other.t or self.title != other.title
