import threading

class ThreadSafeCache:
    def __init__(self, base_cache):
        self.base_cache = base_cache
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            return self.base_cache.get(key)

    def put(self, key, value):
        with self.lock:
            self.base_cache.put(key, value)

    def get_stats(self):
        with self.lock:
            return self.base_cache.get_stats()
