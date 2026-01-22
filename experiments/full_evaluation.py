import sys
import os
import matplotlib.pyplot as plt
import random

# Import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.media_server import MediaServer
from cache.lru_cache import LRUCache

# === CẤU HÌNH THỬ NGHIỆM ===
CACHE_SIZES = [10, 50, 100, 200] # MB
TRACE_LENGTH = 2000              # Số lượng request trong bài test

def generate_viral_trace():
    """Tạo trace có tính chất Viral (Temporal Locality)"""
    trace = []
    # 20% file hot chiếm 80% request
    hot_files = [f"seg_{i:04d}.dat" for i in range(200)] 
    cold_files = [f"seg_{i:04d}.dat" for i in range(200, 1000)]
    
    for _ in range(TRACE_LENGTH):
        if random.random() < 0.8:
            trace.append(random.choice(hot_files))
        else:
            trace.append(random.choice(cold_files))
    return trace

def run_experiment():
    print("🚀 Bắt đầu đánh giá toàn diện (Section 10)...")
    
    # Kết quả để vẽ biểu đồ
    results = {
        'sizes': CACHE_SIZES,
        'hit_ratios': [],
        'avg_latencies': [],
        'p95_latencies': [],
        'bytes_from_disk': [],
        'bytes_from_cache': []
    }

    trace = generate_viral_trace()

    for size_mb in CACHE_SIZES:
        print(f"   ▶ Đang chạy với Cache Size = {size_mb} MB...")
        
        # --- FIX LỖI TẠI ĐÂY ---
        # Code cũ: cache = LRUCache(capacity_items=...) -> SAI
        # Code mới: Truyền thẳng capacity_mb vào
        cache = LRUCache(capacity_mb=size_mb)
        # -----------------------
        
        server = MediaServer("data", cache=cache)
        
        # Chạy Trace
        for seg_id in trace:
            server.get_segment(seg_id)
            
        # Lấy metrics
        m = server.get_metrics()
        results['hit_ratios'].append(m.get('hit_ratio', 0) * 100)
        results['avg_latencies'].append(m.get('avg_latency', 0))
        results['p95_latencies'].append(m.get('p95_latency', 0))
        results['bytes_from_disk'].append(m.get('bytes_disk', 0))
        results['bytes_from_cache'].append(m.get('bytes_cache', 0))

    return results

def plot_charts(res):
    print("📊 Đang vẽ biểu đồ...")
    
    # 1. Hit Ratio vs Cache Size
    plt.figure(figsize=(10, 6))
    plt.plot(res['sizes'], res['hit_ratios'], marker='o', color='g')
    plt.title('Hit Ratio vs Cache Capacity')
    plt.xlabel('Cache Size (MB)')
    plt.ylabel('Hit Ratio (%)')
    plt.grid(True)
    plt.savefig('results/1_hit_ratio.png')
    
    # 2. Latency (Avg & P95) vs Cache Size
    plt.figure(figsize=(10, 6))
    plt.plot(res['sizes'], res['avg_latencies'], marker='o', label='Avg Latency')
    plt.plot(res['sizes'], res['p95_latencies'], marker='x', linestyle='--', label='P95 Latency')
    plt.title('Latency vs Cache Capacity')
    plt.xlabel('Cache Size (MB)')
    plt.ylabel('Latency (ms)')
    plt.legend()
    plt.grid(True)
    plt.savefig('results/2_latency.png')

    # 3. Bytes Read Source (Origin vs Cache)
    plt.figure(figsize=(10, 6))
    indices = range(len(res['sizes']))
    plt.bar(indices, res['bytes_from_disk'], width=0.4, label='From Disk', color='red')
    plt.bar(indices, res['bytes_from_cache'], width=0.4, bottom=res['bytes_from_disk'], label='From Cache', color='blue')
    plt.xticks(indices, res['sizes'])
    plt.title('Data Source: Disk vs Cache')
    plt.xlabel('Cache Size (MB)')
    plt.ylabel('Total MB Transferred')
    plt.legend()
    plt.savefig('results/3_bytes_source.png')

    print("✅ Đã lưu 3 biểu đồ vào thư mục 'results/'")

if __name__ == "__main__":
    if not os.path.exists("results"): os.makedirs("results")
    
    # Đảm bảo có dữ liệu
    if not os.path.exists("data"):
        import subprocess
        subprocess.run(["python3", "generate_data.py"])
        
    data = run_experiment()
    plot_charts(data)
