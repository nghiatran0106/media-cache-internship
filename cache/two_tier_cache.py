from .lru_cache import LRUCache

class TwoTierCache:
    def __init__(self, small_mb, large_mb, threshold_kb=50):
        self.threshold_bytes = threshold_kb * 1024
        self.small_cache = LRUCache(capacity_mb=small_mb)
        self.large_cache = LRUCache(capacity_mb=large_mb)

    def get(self, key):
        val = self.small_cache.get(key)
        if val: return val
        return self.large_cache.get(key)

    def put(self, key, value):
        if len(value) < self.threshold_bytes:
            self.small_cache.put(key, value)
        else:
            self.large_cache.put(key, value)

    def get_stats(self):
        s = self.small_cache.get_stats()
        l = self.large_cache.get_stats()
        return {
            "type": "Two-Tier",
            "hits": s['hits'] + l['hits']
        }
