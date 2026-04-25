import json
import sys


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id") or payload.get("ticker", "user_input")
    data = {
        "company_id": company_id,
        "peer_group": payload.get("peer_group", "待配置可比公司池"),
        "peers": [
            {"ticker": payload.get("ticker", "TBD"), "name": payload.get("company_name", "待分析公司"), "status": "target_company"},
            {"ticker": "TBD", "name": "待补充可比公司", "status": "pending_public_data"},
        ],
        "positioning": "1.0 版本尚未接入可比公司实时数据；请在 1.1 补充同行池和公开行情。",
    }
    print(json.dumps({"status": "ok", "data": data}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
