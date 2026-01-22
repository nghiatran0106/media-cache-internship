import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.media_server import MediaServer
from cache.lru_cache import LRUCache

# Setup: Server CÓ Cache (chứa được 20 items)
cache = LRUCache(capacity_items=20)
server = MediaServer(data_dir="data", cache=cache)

print("=== CHẠY TASK 17.2: LRU CACHE ===")

# Vòng 1: Cold Cache (Chưa có gì)
t1 = time.time()
for i in range(10): 
    server.get_segment(f"seg_{i:04d}.dat")
print(f"Vòng 1 (Cold): {time.time()-t1:.3f}s (Chậm - Đọc đĩa)")

# Vòng 2: Warm Cache (Đã có dữ liệu)
t2 = time.time()
for i in range(10): 
    server.get_segment(f"seg_{i:04d}.dat")
print(f"Vòng 2 (Warm): {time.time()-t2:.3f}s (Nhanh - Cache Hit)")

stats = cache.get_stats()
print(f"Cache Hits:   {stats['hits']} (Kỳ vọng: 10)")
print(f"Cache Misses: {stats['misses']} (Kỳ vọng: 10)")
