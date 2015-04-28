from .event import Event

class ObservableDict:
    def __init__(self, initial_dict):
        if type(initial_dict) != dict:
            raise TypeError('initial_dict must be of type \'dict\', got \'%s\' instead' % type(initial_dict).__name__)
        self.on_added = Event()
        self.on_removed = Event()
        self.dict = initial_dict.copy()

    def add(self, key, item):
        if self.dict.has_key(key):
            raise KeyError('Item with key %s already exists in dictionary.' % key)
        self.dict[key] = item
        self.on_added.fire(self, key, item)
        return item

    def remove(self, key):
        item = self.dict.pop(key)
        self.on_removed.fire(self, key)
        return item
