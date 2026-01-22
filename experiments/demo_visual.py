import sys
import os
import time
import random

# Import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.media_server import MediaServer
from cache.lru_cache import LRUCache

# Màu sắc để in ra terminal đẹp hơn (ANSI colors)
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def simulate_playback(server, trace_name, delay_between_reqs=0.2):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}🎬 PLAYBACK SIMULATION: {trace_name}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{'Segment':<15} | {'Status':<10} | {'Latency':<10} | {'Playback Experience'}")
    print("-" * 75)

    segments = [f"seg_{i:04d}.dat" for i in range(10)] # Xem 10 giây đầu
    
    total_latency = 0
    
    for seg in segments:
        start_t = time.time()
        # Gọi server
        server.get_segment(seg)
        lat = (time.time() - start_t) * 1000 # ms
        total_latency += lat
        
        # Tạo hiệu ứng thị giác
        if lat > 10: # Coi như là MISS (vì đọc đĩa tốn 50ms)
            status = f"{RED}MISS 🐢{RESET}"
            bar = f"{RED}[Buffering...]{RESET}"
            lat_str = f"{lat:.1f}ms"
        else: # HIT
            status = f"{GREEN}HIT  ⚡{RESET}"
            bar = f"{GREEN}[Smooth Play]{RESET}"
            lat_str = f"{lat:.1f}ms"
            
        print(f"{seg:<15} | {status:<19} | {lat_str:<10} | {bar}")
        
        # Delay nhỏ để người xem kịp nhìn thấy dòng chữ chạy (Live trace playback)
        time.sleep(delay_between_reqs)

    print("-" * 75)
    print(f"⏱  Total Buffering Time: {total_latency:.2f} ms\n")

def run_visual_demo():
    # Setup: Cache 50MB
    cache = LRUCache(capacity_mb=50)
    server = MediaServer("data", cache=cache)
    
    # Kịch bản 1: User xem lần đầu (Cache trống)
    # Đây là lúc Cache Warming xảy ra
    print(f"\n{YELLOW}CONTEXT: User watches a video for the first time (Cold Cache){RESET}")
    time.sleep(1)
    simulate_playback(server, "1st VIEWING (Cold Cache)", delay_between_reqs=0.5)
    
    print("\n" + " "*20 + "⬇️  CACHE IS NOW WARMED UP! ⬇️\n")
    time.sleep(2)
    
    # Kịch bản 2: User xem lại (Cache đã có dữ liệu)
    print(f"{YELLOW}CONTEXT: User re-watches the same video (Warm Cache){RESET}")
    time.sleep(1)
    simulate_playback(server, "2nd VIEWING (Warm Cache)", delay_between_reqs=0.2)

if __name__ == "__main__":
    # Đảm bảo dữ liệu tồn tại
    if not os.path.exists("data"):
        import subprocess
        subprocess.run(["python3", "generate_data.py"])
        
    try:
        run_visual_demo()
    except KeyboardInterrupt:
        print("\nStopped.")
