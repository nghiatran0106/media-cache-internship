import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.media_server import MediaServer
from cache.lru_cache import LRUCache
from cache.lfu_cache import LFUCache

def run_workload(cache_type, cache_obj):
    server = MediaServer("data", cache_obj)
    
    # 1. Viral Phase: Xem seg_0000 -> seg_0004 (5 file) NHIỀU LẦN
    for _ in range(10): 
        for i in range(5): server.get_segment(f"seg_{i:04d}.dat")
            
    # 2. Noise Phase: Xem seg_0005 -> seg_0020 (15 file) MỘT LẦN
    # Cache capacity chỉ có 10, nên sẽ phải xóa bớt
    for i in range(5, 20): server.get_segment(f"seg_{i:04d}.dat")
        
    # 3. Return Phase: Quay lại xem viral (0->4)
    # Đây là lúc quyết định thắng thua
    hits_before = cache_obj.get_stats()['hits']
    for i in range(5): server.get_segment(f"seg_{i:04d}.dat")
    hits_after = cache_obj.get_stats()['hits']
    
    return hits_after - hits_before

print("=== CHẠY TASK 17.3: LRU vs LFU ===")
capacity = 10

# Test LRU
lru = LRUCache(capacity)
lru_score = run_workload("LRU", lru)

# Test LFU
lfu = LFUCache(capacity)
lfu_score = run_workload("LFU", lfu)

print(f"Số lần HIT khi quay lại xem video Viral (trên 5 request):")
print(f"LRU: {lru_score}/5 (Thường là 0 - Vì bị video mới đẩy ra)")
print(f"LFU: {lfu_score}/5 (Thường là 5 - Vì video viral tần suất cao được giữ lại)")
