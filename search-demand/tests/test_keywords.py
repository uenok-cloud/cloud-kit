import json, os, sys, tempfile, time, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("CACHE_DIR", tempfile.mkdtemp())
import keywords as K  # noqa: E402


class BuildKeywords(unittest.TestCase):
    def test_main_first_and_unique(self):
        ks = K.build_keywords("千葉市", "外壁塗装", ["外壁塗装 千葉市", "屋根塗装 千葉市"])
        self.assertEqual(ks[0], "外壁塗装 千葉市")
        self.assertEqual(len(ks), len({K.norm(k) for k in ks}))
        self.assertIn("千葉市 外壁塗装", ks)
        self.assertIn("屋根塗装 千葉市", ks)
        self.assertEqual(ks[-1], "外壁塗装")

    def test_service_only(self):
        self.assertEqual(K.build_keywords("", "外壁塗装"), ["外壁塗装"])

    def test_norm(self):
        self.assertEqual(K.norm("外壁塗装　千葉市 "), "外壁塗装 千葉市")


class Prefecture(unittest.TestCase):
    def test_guess(self):
        self.assertEqual(K.guess_prefecture("千葉市"), "千葉県")
        self.assertEqual(K.guess_prefecture("千葉市緑区"), "千葉県")
        self.assertEqual(K.guess_prefecture("東京"), "東京都")
        self.assertEqual(K.guess_prefecture("大阪府"), "大阪府")
        self.assertIsNone(K.guess_prefecture("今治市"))

    def test_match_location(self):
        locs = [
            {"location_code": 1009279, "location_name": "Chiba,Chiba,Japan", "location_type": "City"},
            {"location_code": 20636, "location_name": "Chiba,Japan", "location_type": "Prefecture"},
        ]
        self.assertEqual(K.match_prefecture("Chiba", locs), 20636)
        self.assertIsNone(K.match_prefecture("Tokyo", locs))


class ParseAndCache(unittest.TestCase):
    payload = {"tasks": [{"status_code": 20000, "result": [
        {"keyword": "外壁塗装 千葉市", "search_volume": 720, "competition": "HIGH", "cpc": 1200.5,
         "monthly_searches": [{"year": 2026, "month": 8, "search_volume": 590}, {"year": 2026, "month": 9, "search_volume": 880}]},
        {"keyword": "外壁塗装", "search_volume": 110000, "monthly_searches": []},
    ]}]}

    def test_parse(self):
        v = K.parse_dfs_volumes(self.payload, ["外壁塗装 千葉市", "外壁塗装", "千葉市 外壁塗装 見積り"])
        self.assertEqual(v[K.norm("外壁塗装 千葉市")].volume, 720)
        self.assertEqual(v[K.norm("外壁塗装 千葉市")].latest, 880)
        self.assertIsNone(v[K.norm("千葉市 外壁塗装 見積り")].volume)

    def test_parse_error(self):
        with self.assertRaises(RuntimeError):
            K.parse_dfs_volumes({"tasks": [{"status_code": 40200, "status_message": "Payment Required"}]}, ["a"])

    def test_cache_roundtrip_and_ttl(self):
        c = K.VolumeCache(Path(tempfile.mkdtemp()) / "v.sqlite", ttl=100)
        vols = K.parse_dfs_volumes(self.payload, ["外壁塗装 千葉市"])
        c.put_many(vols, K.JAPAN)
        got = c.get_many(["外壁塗装　千葉市"], K.JAPAN)
        self.assertEqual(got[K.norm("外壁塗装 千葉市")].volume, 720)
        self.assertEqual(c.get_many(["外壁塗装 千葉市"], 20636), {})
        self.assertEqual(c.get_many(["外壁塗装 千葉市"], K.JAPAN, now=time.time() + 1000), {})


class LookupWithoutCredentials(unittest.IsolatedAsyncioTestCase):
    async def test_lookup_returns_rows(self):
        os.environ.pop("DATAFORSEO_LOGIN", None); os.environ.pop("DATAFORSEO_PASSWORD", None)
        async def no_suggest(q, client): return ["外壁塗装 千葉市 助成金"]
        orig = K.google_suggest; K.google_suggest = no_suggest
        try:
            d = await K.lookup("千葉市", "外壁塗装", [], None, K.VolumeCache(Path(tempfile.mkdtemp()) / "v.sqlite"))
        finally:
            K.google_suggest = orig
        self.assertFalse(d["ads_connected"]); self.assertIn("未設定", d["error"])
        self.assertEqual(d["main"]["kw"], "外壁塗装 千葉市"); self.assertEqual(d["pref"], "千葉県")
        self.assertEqual(d["suggest"], ["外壁塗装 千葉市 助成金"])
        json.dumps(d, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
