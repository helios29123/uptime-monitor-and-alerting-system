import json
import time
from checker import probe_url
from notifier import send_alert

# Bộ nhớ lưu trạng thái của tất cả website để đối chiếu giữa các chu kỳ
# Cấu trúc: {"site-google": {"status": "UP", "failures": 0}}
state_store = {}


def load_config():
    """Đọc danh sách website từ file JSON."""
    with open("config/sites.json", "r", encoding="utf-8") as f:
        return json.load(f)


def run_monitor_cycle(targets):
    """Quét qua toàn bộ danh sách và đánh giá trạng thái."""
    for site in targets:
        site_id = site["id"]
        # Ngưỡng chịu đựng lỗi: Mặc định cho phép lỗi 3 lần liên tiếp mới báo sập[cite: 7]
        threshold = site.get("failures_threshold", 3)

        # Khởi tạo trạng thái mặc định cho website mới
        if site_id not in state_store:
            state_store[site_id] = {"status": "UP", "failures": 0}

        current_state = state_store[site_id]

        # 1. Gọi module checker để đo đạc mạng
        result = probe_url(site)

        if result["is_up"]:
            # 2. Logic phục hồi: Đang DOWN mà sống lại -> Bắn thông báo RECOVERED[cite: 7, 10]
            if current_state["status"] == "DOWN":
                print(f"🟢 [PHỤC HỒI] {result['name']} đã trực tuyến trở lại!")
                send_alert(result["name"], result["url"], True, "")
                current_state["status"] = "UP"

            current_state["failures"] = 0
            print(f"🟢 [UP] {result['name']} | Trễ: {result['latency_ms']}ms")

        else:
            # 3. Logic cảnh báo: Đếm số lần lỗi liên tiếp[cite: 7]
            current_state["failures"] += 1
            fails = current_state["failures"]
            print(
                f"⚠️ [CẢNH BÁO] {result['name']} lỗi {fails}/{threshold}: {result['error_type']}"
            )

            # Chỉ bắn Webhook khi chạm ngưỡng và chưa từng báo DOWN trước đó[cite: 7]
            if fails >= threshold and current_state["status"] == "UP":
                print(
                    f"🔴 [SẬP] Đã xác nhận downtime cho {result['name']}. Đang bắn cảnh báo..."
                )
                send_alert(result["name"], result["url"], False, result["message"])
                current_state["status"] = "DOWN"


if __name__ == "__main__":
    print("🚀 Khởi động hệ thống Uptime Monitor & Alerting System...")
    targets = load_config()

    try:
        # Vòng lặp vĩnh cửu đóng vai trò như Cron Job[cite: 9]
        while True:
            print(f"\n--- 🔄 Bắt đầu chu kỳ quét: {time.strftime('%H:%M:%S')} ---")
            run_monitor_cycle(targets)

            # Nghỉ 10 giây trước khi quét vòng tiếp theo (bạn có thể chỉnh lên 60s trong thực tế)
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng hệ thống giám sát an toàn.")
