class LFUCache:
    def __init__(self, capacity_mb):
        self.capacity_bytes = capacity_mb * 1024 * 1024
        self.current_size = 0
        self.cache = {} # key -> data
        self.freq = {}  # key -> count
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.cache:
            self.hits += 1
            self.freq[key] += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key, value):
        size = len(value)
        if size > self.capacity_bytes: return

        if key in self.cache:
            self.current_size -= len(self.cache[key])
            self.cache[key] = value
            self.freq[key] += 1
            self.current_size += size
        else:
            while self.current_size + size > self.capacity_bytes:
                # Tìm key có freq thấp nhất để xóa (Simple LFU)
                victim = min(self.freq, key=self.freq.get)
                self.current_size -= len(self.cache[victim])
                del self.cache[victim]
                del self.freq[victim]
            
            self.cache[key] = value
            self.freq[key] = 1
            self.current_size += size

    def get_stats(self):
        return {"type": "LFU", "hits": self.hits}
