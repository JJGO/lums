import time

class CacheQuery:

    def __init__(self, query):
        self.state = 'Never'
        self.query = query
        self.last_contact = None
        self.last_query = None

    def run(self):
        q = self.query.run()
        if q is not None:
            self.state = 'Up'
            self.last_contact = time.time()
            self.last_query = q
        if q is None:
            self.state = 'Down'

        # TODO consider how to implement state = Timeout

        return q, self.state, self.last_contact
