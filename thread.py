import threading


class Thread(threading.Thread):
	# Вспомогательный класс, который используется для короткой инициализации потока
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()