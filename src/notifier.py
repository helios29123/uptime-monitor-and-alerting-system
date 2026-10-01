import os
import httpx
from dotenv import load_dotenv

# Tìm và nạp các biến môi trường từ file src/.env
load_dotenv("src/.env")

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_alert(title: str, message: str, is_up: bool):
    """Gửi thông báo trạng thái lên Discord qua Webhook."""
    if not WEBHOOK_URL:
        print("⚠️ Lỗi: Chưa cấu hình DISCORD_WEBHOOK_URL trong file .env")
        return

    # Màu sắc: Xanh lá (UP) và Đỏ (DOWN)
    color = 65280 if is_up else 16711680

    payload = {"embeds": [{"title": title, "description": message, "color": color}]}

    try:
        # Gửi payload JSON đến kênh chat với timeout 5s[cite: 3]
        response = httpx.post(WEBHOOK_URL, json=payload, timeout=5.0)
        if response.status_code in (200, 204):
            print(f"Đã bắn cảnh báo '{title}' thành công.")
        else:
            print(f"⚠️ Thất bại. Máy chủ trả về mã HTTP: {response.status_code}")
    except Exception as exc:
        print(f"⚠️ Lỗi mạng khi gọi Webhook: {exc}")


if __name__ == "__main__":
    print("--- KIỂM TRA LUỒNG THÔNG BÁO ---")
    send_alert("Google Vietnam", "https://www.google.com.vn", True)
    send_alert(
        "Dịch vụ Nội bộ",
        "https://api.internal",
        False,
        "CONNECTION_REFUSED - Không thể kết nối",
    )
