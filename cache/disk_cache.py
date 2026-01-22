import os
import shutil

class DiskCache:
    def __init__(self, cache_dir="/tmp/media_cache_project"):
        """
        Khởi tạo Cache lưu trên ổ cứng.
        Mặc định lưu tại /tmp/media_cache_project
        """
        self.cache_dir = cache_dir
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.hits = 0
        self.misses = 0

    def get(self, key):
        """Đọc file từ ổ cứng"""
        path = os.path.join(self.cache_dir, key)
        
        if os.path.exists(path):
            self.hits += 1
            try:
                with open(path, 'rb') as f:
                    return f.read()
            except Exception:
                return None
        
        self.misses += 1
        return None

    def put(self, key, value):
        """Ghi file xuống ổ cứng"""
        # --- QUAN TRỌNG: Tự động tạo lại thư mục nếu nó bị xóa ---
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        # ---------------------------------------------------------

        path = os.path.join(self.cache_dir, key)
        try:
            with open(path, 'wb') as f:
                f.write(value)
        except Exception as e:
            print(f"Error writing disk cache: {e}")

    def clear(self):
        """Xóa toàn bộ cache trên đĩa"""
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir, ignore_errors=True)

    def get_stats(self):
        return {
            "type": "DiskPersistence",
            "hits": self.hits,
            "misses": self.misses
        }
