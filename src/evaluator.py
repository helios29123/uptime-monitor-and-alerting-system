import time
from src.notifier import send_discord_alert

def evaluate_and_alert(site_id: str, result: dict, threshold: int, state_store: dict):
    """
    Xử lý logic chống báo động giả, đếm số lần lỗi liên tiếp và kích hoạt cảnh báo.
    """
    # Khởi tạo trạng thái mặc định nếu website mới được thêm vào
    if site_id not in state_store:
        state_store[site_id] = {"consecutive_failures": 0, "status": "UP"}
        
    current_state = state_store[site_id]
    timestamp = time.strftime("%H:%M:%S")
    
    if result["is_up"]:
        # Logic phục hồi: Nếu trạng thái trước đó là DOWN, nay UP trở lại[cite: 2]
        if current_state["status"] == "DOWN":
            print(f"[{timestamp}] 🟢 [RECOVERED] {result['name']} đã trực tuyến!")
            send_discord_alert(
                title=f"PHỤC HỒI: {result['name']}",
                message=f"Dịch vụ đã hoạt động bình thường. Độ trễ: {result['latency_ms']}ms",
                is_up=True
            )
            current_state["status"] = "UP"
            
        current_state["consecutive_failures"] = 0
        print(f"[{timestamp}] 🟢 [UP] {result['name']} - Trễ: {result['latency_ms']}ms")
        
    else:
        # Logic lỗi: Tăng biến đếm và đánh giá ngưỡng sập (Threshold)
        current_state["consecutive_failures"] += 1
        fails = current_state["consecutive_failures"]
        
        print(f"[{timestamp}] ⚠️ [LỖI] {result['name']} ({fails}/{threshold}): {result['error_type']}")
        
        # Chỉ bắn cảnh báo nếu chạm ngưỡng (thất bại liên tiếp >= threshold) và trước đó chưa báo DOWN[cite: 2, 8]
        if fails >= threshold and current_state["status"] == "UP":
            print(f"[{timestamp}] 🔴 [SẬP] Xác nhận {result['name']} đã sập!")
            send_discord_alert(
                title=f"SẬP HỆ THỐNG: {result['name']}",
                message=f"**Lỗi:** {result['error_type']}\n**Chi tiết:** {result['message']}",
                is_up=False
            )
            current_state["status"] = "DOWN"