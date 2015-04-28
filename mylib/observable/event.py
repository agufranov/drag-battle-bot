import threading


class Event:
	def __init__(self):
		self._lock = threading.RLock()
		self._handlers = {}
		self._new_handler_id = 0

	def add_handler(self, func):
		with self._lock:
			self._handlers[self._new_handler_id] = func
			result = self._new_handler_id
			self._new_handler_id += 1
			return result

	def remove_handler(self, handler_id):
		with self._lock:
			self._handlers.pop(handler_id)

	def fire(self, *args):
		with self._lock:
			for i in self._handlers:
				self._handlers[i](*args)
