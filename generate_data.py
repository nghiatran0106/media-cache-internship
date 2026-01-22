import os
import random

DATA_DIR = "data"
NUM_SEGMENTS = 500       # 500 đoạn video
SEGMENT_SIZE_KB = 100    # Mỗi đoạn 100KB

def create_dummy_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    print(f"⏳ Đang tạo {NUM_SEGMENTS} file tại '{DATA_DIR}'...")
    for i in range(NUM_SEGMENTS):
        with open(os.path.join(DATA_DIR, f"seg_{i:04d}.dat"), 'wb') as f:
            f.write(os.urandom(SEGMENT_SIZE_KB * 1024))
    print("✅ Xong!")

if __name__ == "__main__":
    create_dummy_data()
