from .event import Event


class ObservableProperty:
    def __init__(self, value=None):
        self.value = value
        self.on_changed = Event()

    def set_value(self, new_value):
        if self.value != new_value:
            old_value = self.value
            self.value = new_value
            self.on_changed.fire(self.value, old_value)

    def get_value(self):
        return self.value

    def __str__(self):
        return self.value.__str__()
