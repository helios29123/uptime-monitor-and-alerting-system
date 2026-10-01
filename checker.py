import time
import httpx
from typing import Any, Dict


def probe_url(target: Dict[str, Any]) -> Dict[str, Any]:
    """Gửi HTTP GET đến endpoint, đo latency và bắt ngoại lệ mạng."""
    url = target["url"]
    timeout_sec = float(target.get("timeout", 5.0))

    # Cấu trúc dữ liệu trả về chuẩn hóa
    result = {
        "id": target.get("id"),
        "name": target.get("name"),
        "url": url,
        "is_up": False,
        "status_code": None,
        "latency_ms": 0.0,
        "error_type": None,
        "message": "",
    }

    start_time = time.perf_counter()
    try:
        timeout_config = httpx.Timeout(timeout_sec, connect=timeout_sec)

        with httpx.Client(timeout=timeout_config, follow_redirects=True) as client:
            response = client.get(url)
            latency = (time.perf_counter() - start_time) * 1000

            result["status_code"] = response.status_code
            result["latency_ms"] = round(latency, 2)

            if 200 <= response.status_code < 400:
                result["is_up"] = True
                result["message"] = "Service Operational"
            else:
                result["is_up"] = False
                result["error_type"] = f"HTTP_{response.status_code}"
                result["message"] = f"Received status code {response.status_code}"

    except httpx.ConnectTimeout:
        result["error_type"] = "TIMEOUT"
        result["message"] = f"Connection timed out after {timeout_sec}s"
    except httpx.ReadTimeout:
        result["error_type"] = "READ_TIMEOUT"
        result["message"] = f"Server did not respond within {timeout_sec}s"
    except httpx.ConnectError:
        result["error_type"] = "CONNECTION_REFUSED"
        result["message"] = "Cannot resolve domain or connection was refused"
    except httpx.HTTPError as exc:
        result["error_type"] = "NETWORK_ERROR"
        result["message"] = str(exc)
    except Exception as exc:
        result["error_type"] = "UNEXPECTED_ERROR"
        result["message"] = str(exc)

    return result


# Phần test chạy cục bộ
if __name__ == "__main__":
    import json

    with open("config/sites.json", "r", encoding="utf-8") as f:
        targets = json.load(f)

    print("--- BẮT ĐẦU HEALTH CHECK ---")
    for site in targets:
        res = probe_url(site)
        status_tag = "UP" if res["is_up"] else "DOWN"
        print(f"[{status_tag}] {res['name']} ({res['url']})")
        print(f"  - Status Code : {res['status_code']}")
        print(f"  - Latency     : {res['latency_ms']} ms")
        if not res["is_up"]:
            print(f"  - Error       : {res['error_type']} -> {res['message']}")
        print("-" * 40)
