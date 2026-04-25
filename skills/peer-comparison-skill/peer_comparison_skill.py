import json
import sys


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id", "asiasoft_1675_hk")
    data = {
        "company_id": company_id,
        "peer_group": "通信软件与企业数字化",
        "peers": [
            {"ticker": "1675.HK", "name": "亚信科技", "status": "seed_company"},
            {"ticker": "TBD", "name": "待补充可比公司", "status": "pending_public_data"},
        ],
        "positioning": "1.0 版本尚未接入可比公司实时数据；请在 1.1 补充同行池和公开行情。",
    }
    print(json.dumps({"status": "ok", "data": data}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
