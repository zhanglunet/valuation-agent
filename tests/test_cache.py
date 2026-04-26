import tempfile
import unittest
from pathlib import Path

from valuation_agent import cache


class CacheTests(unittest.TestCase):
    def test_write_and_read_cache(self):
        original_root = cache.CACHE_ROOT
        with tempfile.TemporaryDirectory() as temp_dir:
            cache.CACHE_ROOT = Path(temp_dir)
            cache.write_cache("unit", "https://example.com/a", {"ok": True})
            self.assertEqual(cache.read_cache("unit", "https://example.com/a"), {"ok": True})
        cache.CACHE_ROOT = original_root

    def test_expired_cache_returns_none(self):
        original_root = cache.CACHE_ROOT
        with tempfile.TemporaryDirectory() as temp_dir:
            cache.CACHE_ROOT = Path(temp_dir)
            cache.write_cache("unit", "expired", {"ok": True})
            self.assertIsNone(cache.read_cache("unit", "expired", ttl_seconds=0))
        cache.CACHE_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
