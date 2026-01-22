import sys
import os
import time
import threading

# Import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.media_server import MediaServer
from cache.lru_cache import LRUCache
from cache.two_tier_cache import TwoTierCache
from cache.thread_safe_wrapper import ThreadSafeCache

def test_prefetching():
    print("\n=== TEST 1: PREFETCHING (Task 17.5) ===")
    # Cache nhỏ, bật prefetch
    cache = LRUCache(capacity_mb=10)
    server = MediaServer("data", cache=cache, prefetch_enabled=True)
    
    # Request seg_0000 -> Server tự ngầm load seg_0001
    print("1. User request seg_0000 (Miss -> Đọc đĩa 50ms)")
    t0 = time.time()
    server.get_segment("seg_0000.dat")
    print(f"   Done in {(time.time()-t0)*1000:.1f}ms")
    
    # Cho thread prefetch chạy xong (sleep xíu)
    time.sleep(0.1) 
    
    # Request seg_0001 -> Lúc này nó ĐÃ NẰM TRONG CACHE rồi!
    print("2. User request seg_0001 (Kỳ vọng: HIT siêu nhanh nhờ Prefetch)")
    t1 = time.time()
    server.get_segment("seg_0001.dat")
    dt = (time.time()-t1)*1000
    print(f"   Done in {dt:.1f}ms")
    
    if dt < 10:
        print("✅ PREFETCH THÀNH CÔNG!")
    else:
        print("❌ PREFETCH THẤT BẠI (Vẫn chậm)")

def test_concurrency():
    print("\n=== TEST 2: CONCURRENCY (Task 17.6) ===")
    # Dùng Wrapper ThreadSafe
    unsafe_cache = LRUCache(capacity_mb=50)
    safe_cache = ThreadSafeCache(unsafe_cache)
    server = MediaServer("data", cache=safe_cache)
    
    def client_worker(cid):
        for i in range(50): # Mỗi client gọi 50 request
            server.get_segment(f"seg_{i:04d}.dat")
            
    threads = []
    print("🚀 Đang chạy 20 Client cùng lúc...")
    start_t = time.time()
    
    for i in range(20):
        t = threading.Thread(target=client_worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print(f"✅ Hoàn thành 1000 requests trong {time.time()-start_t:.2f}s")
    print("Stats:", safe_cache.get_stats())

def test_two_tier():
    print("\n=== TEST 3: TWO-TIER CACHE (Task 17.4) ===")
    # Small Cache: 1MB (cho thumb), Large Cache: 50MB (cho video)
    tier_cache = TwoTierCache(small_mb=1, large_mb=50)
    
    # Giả lập:
    # seg_xxxx.dat (100KB) -> Vào Large Cache
    # thumb_xxxx.dat (10KB) -> Vào Small Cache
    
    print("Put 'thumb_01' (Small) và 'seg_01' (Large)...")
    tier_cache.put("thumb_01", b"x"*10240) # 10KB
    tier_cache.put("seg_01", b"x"*102400) # 100KB
    
    print("Get 'thumb_01':", "HIT" if tier_cache.get("thumb_01") else "MISS")
    print("Get 'seg_01':  ", "HIT" if tier_cache.get("seg_01") else "MISS")

if __name__ == "__main__":
    # Tạo dữ liệu nếu chưa có
    if not os.path.exists("data"):
        import subprocess
        subprocess.run(["python3", "generate_data.py"])

    test_two_tier()
    test_prefetching()
    test_concurrency()
