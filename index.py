import json
import time
from src.checker import probe_url
from src.evaluator import evaluate_and_alert

# Bộ nhớ lưu trạng thái của toàn bộ hệ thống
state_store = {}

def load_targets():
    with open("config/sites.json", "r", encoding="utf-8") as f:
        return json.load(f)

def monitor_cycle():
    targets = load_targets()
    
    for site in targets:
        site_id = site["id"]
        threshold = site.get("fail_threshold", 3)
        
        # 1. Gọi checker để đo đạc mạng[cite: 2]
        result = probe_url(site)
        
        # 2. Chuyển kết quả qua evaluator để đánh giá và báo động[cite: 2]
        evaluate_and_alert(site_id, result, threshold, state_store)

if __name__ == "__main__":
    print("🚀 Khởi động Hệ Thống Giám Sát Uptime (Modular Architecture)...")
    try:
        # Vòng lặp đóng vai trò như Cron Job chạy định kỳ[cite: 2, 8]
        while True:
            print("\n" + "="*40)
            monitor_cycle()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Đã tắt hệ thống giám sát.")