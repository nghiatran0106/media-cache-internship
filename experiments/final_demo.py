import sys
import os
import time
import threading

# --- SETUP PATH ---
# Thêm đường dẫn cha để import được các module trong project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.media_server import MediaServer
from cache.lru_cache import LRUCache
from cache.lfu_cache import LFUCache
from cache.two_tier_cache import TwoTierCache
from cache.thread_safe_wrapper import ThreadSafeCache
from cache.disk_cache import DiskCache

# --- SETUP DATA ---
# Tự động tạo dữ liệu nếu chưa có
if not os.path.exists("data"):
    print("⚠ Data not found. Generating dummy data...")
    import subprocess
    subprocess.run(["python3", "generate_data.py"])

def print_header(task_name):
    print("\n" + "="*70)
    print(f"🎬 DEMO: {task_name}")
    print("="*70)

# ==========================================
# TASK 17.1: BASELINE (NO CACHE)
# ==========================================
def demo_17_1():
    print_header("Task 17.1 - Baseline (No Cache)")
    server = MediaServer("data", cache=None)
    
    print("Requesting 5 segments (Cold)...")
    t0 = time.time()
    for i in range(5): 
        server.get_segment(f"seg_{i:04d}.dat")
    dt = time.time() - t0
    
    print(f"Time taken: {dt:.3f}s")
    print(f"Avg Latency: {dt/5*1000:.1f}ms (Expected ~50ms per req)")

# ==========================================
# TASK 17.2: LRU CACHE (WARMING)
# ==========================================
def demo_17_2():
    print_header("Task 17.2 - LRU Cache Warming")
    # Cache 10MB
    cache = LRUCache(capacity_mb=10)
    server = MediaServer("data", cache=cache)
    
    print("1. Cold Run (First access - Miss)...")
    t0 = time.time()
    for i in range(5): server.get_segment(f"seg_{i:04d}.dat")
    print(f"   Time: {time.time()-t0:.3f}s")
    
    print("2. Warm Run (Second access - Hit)...")
    t0 = time.time()
    for i in range(5): server.get_segment(f"seg_{i:04d}.dat")
    dt = time.time()-t0
    print(f"   Time: {dt:.3f}s")
    
    if dt < 0.01:
        print("✅ Result: CACHE HIT (Zero Latency)")
    else:
        print("❌ Result: CACHE MISS (Still Slow)")

# ==========================================
# TASK 17.3: LRU vs LFU (EVICTION POLICY)
# ==========================================
def demo_17_3():
    print_header("Task 17.3 - Eviction Policy (Viral Workload)")
    
    # Cấu hình Cache siêu nhỏ (0.01MB ~ 10KB) để ép Eviction xảy ra nhanh
    capacity = 0.01 
    lru = LRUCache(capacity_mb=capacity)
    lfu = LFUCache(capacity_mb=capacity)
    
    print(f"Cache Capacity: {capacity} MB (~10KB)")

    def run_trace(cache_obj, name):
        # 1. Viral Item: 1KB (Put vào và Access nhiều lần)
        viral_key = "seg_viral"
        data = b"x" * 1024 # 1KB
        cache_obj.put(viral_key, data)
        # Tăng frequency (quan trọng cho LFU)
        for _ in range(10): cache_obj.get(viral_key)
        
        # 2. Noise Items: Đẩy vào 20 items mới (Tổng 20KB > 10KB Capacity)
        # Điều này sẽ ép Cache phải xóa bớt dữ liệu cũ
        for i in range(20):
            cache_obj.put(f"noise_{i}", b"x" * 1024)
            
        # 3. Kiểm tra xem Viral Item còn sống sót không?
        is_alive = cache_obj.get(viral_key) is not None
        return is_alive

    lru_result = run_trace(lru, "LRU")
    lfu_result = run_trace(lfu, "LFU")
    
    print(f"LRU keeps viral item? {lru_result} (Expect: False - pushed out by recency)")
    print(f"LFU keeps viral item? {lfu_result} (Expect: True - kept by frequency)")
    
    if not lru_result and lfu_result:
        print("✅ LOGIC CORRECT: LFU wins on viral workload.")
    else:
        print("⚠ LOGIC CHECK: Something is unexpected.")

# ==========================================
# TASK 17.4: TWO TIER CACHE
# ==========================================
def demo_17_4():
    print_header("Task 17.4 - Two Tier Cache")
    # Small < 50KB, Large >= 50KB
    tier = TwoTierCache(small_mb=1, large_mb=10, threshold_kb=50)
    
    print("Putting 'thumb_1' (10KB) -> Should go to Small Tier")
    tier.put("thumb_1", b"x"*10240) 
    
    print("Putting 'seg_1' (100KB) -> Should go to Large Tier")
    tier.put("seg_1", b"x"*102400)
    
    stats = tier.get_stats()
    # Kiểm tra xem dữ liệu có nằm đúng chỗ không
    # (Lưu ý: Bạn cần đảm bảo TwoTierCache trả về internal stats hoặc check thủ công)
    
    # Hack nhẹ để check: truy cập vào biến private của class con
    s_size = tier.small_cache.current_size_bytes
    l_size = tier.large_cache.current_size_bytes
    
    print(f"Small Cache Size: {s_size} bytes")
    print(f"Large Cache Size: {l_size} bytes")
    
    if s_size > 0 and l_size > 0:
        print("✅ ROUTING CORRECT: Data split into tiers.")
    else:
        print("❌ ROUTING FAILED.")

# ==========================================
# TASK 17.5: PREFETCHING
# ==========================================
def demo_17_5():
    print_header("Task 17.5 - Prefetching")
    cache = LRUCache(capacity_mb=10)
    # Bật tính năng prefetch
    server = MediaServer("data", cache=cache, prefetch_enabled=True)
    
    print("1. User requests seg_0010.dat...")
    server.get_segment("seg_0010.dat")
    # Server sẽ ngầm trigger load seg_0011.dat
    
    print("   (Waiting 0.2s for background thread)...")
    time.sleep(0.2)
    
    print("2. User requests seg_0011.dat (Expect Hit)...")
    t0 = time.time()
    server.get_segment("seg_0011.dat")
    dt = (time.time() - t0) * 1000
    
    print(f"   Latency: {dt:.2f} ms")
    if dt < 10:
        print("✅ PREFETCH SUCCESS")
    else:
        print("❌ PREFETCH FAILED (Too slow)")

# ==========================================
# TASK 17.6: CONCURRENCY
# ==========================================
def demo_17_6():
    print_header("Task 17.6 - Concurrency (20 Clients)")
    # Dùng ThreadSafe Wrapper
    safe_cache = ThreadSafeCache(LRUCache(capacity_mb=50))
    server = MediaServer("data", cache=safe_cache)
    
    def client_worker():
        # Tất cả client cùng request 1 tập hợp key giống nhau để tạo Hit
        for i in range(10): 
            server.get_segment(f"seg_{i:04d}.dat")

    threads = []
    print("🚀 Launching 20 threads...")
    t0 = time.time()
    
    for _ in range(20):
        t = threading.Thread(target=client_worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print(f"Finished in {time.time()-t0:.2f}s")
    
    stats = safe_cache.get_stats()
    print(f"Final Stats: {stats}")
    
    if stats['hits'] > 0:
        print("✅ INTEGRITY CHECK: System survived concurrency.")
    else:
        print("⚠ CHECK: Hits = 0 (Possible race condition or cold cache only)")

# ==========================================
# TASK 17.7: PERSISTENCE
# ==========================================
def demo_17_7():
    print_header("Task 17.7 - Disk Persistence")
    d_cache = DiskCache()
    d_cache.clear() # Xóa sạch cũ
    
    key = "saved_segment"
    val = b"IMPORTANT_VIDEO_DATA"
    
    print("1. Server writes to disk cache...")
    d_cache.put(key, val)
    
    print("2. Server restarts (New Object)...")
    new_d_cache = DiskCache()
    
    print("3. Reading from disk...")
    recovered_val = new_d_cache.get(key)
    
    if recovered_val == val:
        print(f"   Read Back: {len(recovered_val)} bytes matched.")
        print("✅ PERSISTENCE SUCCESS")
    else:
        print("❌ DATA LOST")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    try:
        demo_17_1()
        demo_17_2()
        demo_17_3()
        demo_17_4()
        demo_17_5()
        demo_17_6()
        demo_17_7()
        
        print("\n" + "="*70)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
