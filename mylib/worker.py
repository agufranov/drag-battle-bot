import threading


class Worker:
	def __init__(self, func):
		self.func = func

	def __call__(self, *args, **kwargs):
		self.event = threading.Event()
		self.thread = threading.Thread(target=self.func, args=args+(self.event,))
		return self

	def start(self):
		self.thread.start()

	def stop(self):
		self.event.set()
		#if threading.current_thread().ident != self.thread.ident:
			#self.thread.join()
		

if __name__ == '__main__':
	class A:
		def __init__(self):
			pass

		@Worker
		def loop(self, x, e):
			while 1:
				if e.is_set():
					break
				print x, self
				e.wait(1)

	a = A()
	w = A.loop(a, 8)
	w.start()
	import msvcrt
	msvcrt.getch()
	w.stop()
