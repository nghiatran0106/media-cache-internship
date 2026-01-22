import os
import time
import threading
import numpy as np

class MediaServer:
    def __init__(self, data_dir, cache=None, disk_latency=0.05, prefetch_enabled=False):
        self.data_dir = data_dir
        self.cache = cache
        self.disk_latency = disk_latency
        self.prefetch_enabled = prefetch_enabled
        
        # INSTRUMENTATION
        self.stats = {
            'requests': 0,
            'disk_reads': 0,
            'bytes_disk': 0,
            'bytes_cache': 0,
            'latencies': []
        }
        # Thêm Lock để an toàn khi chạy đa luồng (Task 17.6)
        self.lock = threading.Lock()

    def get_segment(self, segment_id):
        with self.lock:
            self.stats['requests'] += 1
        
        start_t = time.time()
        data = None

        # 1. Check Cache
        if self.cache:
            data = self.cache.get(segment_id)
            if data:
                with self.lock:
                    self.stats['bytes_cache'] += len(data)

        # 2. Disk Read (Miss)
        if not data:
            data = self._read_from_disk(segment_id)

        # 3. Prefetching Logic (Task 17.5)
        if self.prefetch_enabled and data:
            self._trigger_prefetch(segment_id)

        # 4. Record Latency
        latency = (time.time() - start_t) * 1000 # ms
        with self.lock:
            self.stats['latencies'].append(latency)
        
        return data

    def _trigger_prefetch(self, current_id):
        try:
            # Parse: seg_0005.dat -> 5
            curr_idx = int(current_id.split('_')[1].split('.')[0])
            next_id = f"seg_{curr_idx + 1:04d}.dat"
            
            # Chạy thread ngầm
            threading.Thread(target=self._prefetch_task, args=(next_id,)).start()
        except (IndexError, ValueError):
            pass

    def _prefetch_task(self, segment_id):
        """Hàm chạy ngầm: Load file vào Cache"""
        # Chỉ prefetch nếu Cache chưa có
        if self.cache and not self.cache.get(segment_id):
            # Đọc đĩa (bypass thống kê request chính)
            filepath = os.path.join(self.data_dir, segment_id)
            if os.path.exists(filepath):
                # Vẫn sleep để giả lập disk load
                time.sleep(self.disk_latency) 
                with open(filepath, 'rb') as f:
                    data = f.read()
                if self.cache:
                    self.cache.put(segment_id, data)

    def _read_from_disk(self, segment_id):
        # Giả lập độ trễ
        time.sleep(self.disk_latency)
        
        filepath = os.path.join(self.data_dir, segment_id)
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            with self.lock:
                self.stats['disk_reads'] += 1
                self.stats['bytes_disk'] += len(data)
                
            # Put vào cache
            if self.cache: 
                self.cache.put(segment_id, data)
            return data
        except FileNotFoundError:
            return None

    def get_metrics(self):
        with self.lock:
            lats = self.stats['latencies']
            if not lats: return {}
            
            return {
                'avg_latency': np.mean(lats),
                'p95_latency': np.percentile(lats, 95),
                'bytes_disk': self.stats['bytes_disk'] / (1024*1024),
                'bytes_cache': self.stats['bytes_cache'] / (1024*1024),
                'hit_ratio': 1.0 - (self.stats['disk_reads'] / self.stats['requests']) if self.stats['requests'] > 0 else 0
            }

