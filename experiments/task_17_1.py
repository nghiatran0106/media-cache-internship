import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.media_server import MediaServer

# Setup: Server KHÔNG Cache
server = MediaServer(data_dir="data", cache=None)

print("=== CHẠY TASK 17.1: BASELINE (NO CACHE) ===")
start_time = time.time()

# Client request 10 file
for i in range(10):
    server.get_segment(f"seg_{i:04d}.dat")

total_time = time.time() - start_time
stats = server.get_stats()

print(f"Tổng thời gian: {total_time:.3f}s")
print(f"Avg Latency:    {total_time/10*1000:.1f} ms/req")
print(f"Disk Reads:     {stats['disk_reads']} (Kỳ vọng: 10)")
