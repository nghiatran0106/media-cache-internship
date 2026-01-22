from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity_mb):
        # Chuyển đổi MB sang Bytes
        self.capacity_bytes = capacity_mb * 1024 * 1024
        self.current_size_bytes = 0
        self.cache = OrderedDict()
        
        # Stats
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key):
        if key not in self.cache:
            self.misses += 1
            return None
        
        self.hits += 1
        self.cache.move_to_end(key) # Move to MRU (Most Recently Used)
        return self.cache[key]

    def put(self, key, value):
        size = len(value)
        
        # Nếu item lớn hơn cả cái cache thì bỏ qua
        if size > self.capacity_bytes:
            return

        # Nếu key đã có, update và trừ size cũ
        if key in self.cache:
            self.current_size_bytes -= len(self.cache[key])
            self.cache.move_to_end(key)
        else:
            # Nếu chưa có, kiểm tra xem có cần Evict (xóa bớt) không
            while self.current_size_bytes + size > self.capacity_bytes:
                # Xóa phần tử cũ nhất (đầu hàng đợi)
                if not self.cache: break
                _, evicted_val = self.cache.popitem(last=False)
                self.current_size_bytes -= len(evicted_val)
                self.evictions += 1
        
        # Thêm mới
        self.cache[key] = value
        self.current_size_bytes += size

    def get_stats(self):
        total = self.hits + self.misses
        hit_ratio = (self.hits / total) if total > 0 else 0
        return {
            "type": "LRU",
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_ratio": hit_ratio,
            "current_size_mb": self.current_size_bytes / (1024*1024)
        }
