from concurrent.futures import ThreadPoolExecutor, wait

class ParallelQuery:

    def __init__(self, queries):
        self.queries = queries

    def run(self):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(q.run) for q in self.queries.values()]
            wait(futures)
        queries = {k: f.result() for k, f in zip(self.queries, futures)}
        return queries

