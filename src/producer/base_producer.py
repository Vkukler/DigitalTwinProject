import threading

class BaseProducer:
    def __init__(self, publisher):
        self.publisher = publisher

    def run(self):
        """Override in subclass"""
        raise NotImplementedError

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
