from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from urllib.parse import quote

from .paths import DATA_DIR


CACHE_ROOT = DATA_DIR / "raw"
DEFAULT_TTL_SECONDS = 24 * 60 * 60


def _cache_path(namespace: str, key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
    return CACHE_ROOT / namespace / f"{quote(digest)}.json"


def read_cache(namespace: str, key: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict | None:
    path = _cache_path(namespace, key)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    created_at = payload.get("created_at", 0)
    if ttl_seconds is not None and time.time() - created_at > ttl_seconds:
        return None
    return payload.get("data")


def write_cache(namespace: str, key: str, data: dict) -> None:
    path = _cache_path(namespace, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at": time.time(),
        "key": key,
        "data": data,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
