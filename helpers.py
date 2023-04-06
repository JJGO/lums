"""A simple implementation of a LRU dict that supports discarding by maximum
capacity and by maximum time not being used."""

import time
from collections import OrderedDict


class LRUDict(OrderedDict):
    """An dict that can discard least-recently-used items, either by maximum capacity
    or by time to live.
    An item's ttl is refreshed (aka the item is considered "used") by direct access
    via [] or get() only, not via iterating over the whole collection with items()
    for example.
    Expired entries only get purged after insertions or changes. Either call purge()
    manually or check an item's ttl with ttl() if that's unacceptable.
    """

    def __init__(self, *args, maxduration=None, maxsize=128, **kwargs):
        """Same arguments as OrderedDict with these 2 additions:
        maxduration: number of seconds entries are kept. 0 or None means no timelimit.
        maxsize: maximum number of entries being kept."""
        super().__init__(*args, **kwargs)
        self.maxduration = maxduration
        self.maxsize = maxsize
        self.purge()

    def purge(self):
        """Removes expired or overflowing entries."""
        if self.maxsize:
            # pop until maximum capacity is reached
            overflowing = max(0, len(self) - self.maxsize)
            for _ in range(overflowing):
                self.popitem(last=False)
        if self.maxduration:
            # expiration limit
            limit = time.time() - self.maxduration
            # as long as there are still items in the dictionary
            while self:
                # look at the oldest (front)
                _, lru = next(iter(super().values()))
                # if it is within the timelimit, we're fine
                if lru > limit:
                    break
                # otherwise continue to pop the front
                self.popitem(last=False)

    def __getitem__(self, key):
        # retrieve item
        value = super().__getitem__(key)[0]
        # update lru time
        super().__setitem__(key, (value, time.time()))
        self.move_to_end(key)
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def ttl(self, key):
        """Returns the number of seconds this item will live.
        The item might still be deleted if maxsize is reached.
        The time to live can be negative, as for expired items
        that have not been purged yet."""
        if self.maxduration:
            lru = super().__getitem__(key)[1]
            return self.maxduration - (time.time() - lru)

    def __setitem__(self, key, value):
        super().__setitem__(key, (value, time.time()))
        self.purge()

    def items(self):
        # remove ttl from values
        return ((k, v) for k, (v, _) in super().items())

    def values(self):
        # remove ttl from values
        return (v for v, _ in super().values())


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError("Singletons must be accessed through `instance()`.")

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
