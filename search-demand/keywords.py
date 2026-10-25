"""検索ボリューム表示ツールの中身（キーワード生成・Google候補・DataForSEO・キャッシュ）。

商談中に「○○市で○○を検索している人は月にこれくらい」を数秒で出すための部品。
数字の出どころは Google 広告のキーワードプランナーと同じデータ（DataForSEO 経由）。
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import httpx

JAPAN = 2392  # DataForSEO / Google 広告の「日本」の location_code
CACHE_DIR = Path(os.environ.get("CACHE_DIR", Path(__file__).parent / "cache"))
VOLUME_TTL_SEC = 30 * 24 * 3600  # 月次データなので 30 日は同じ数字を返す
DFS_BASE = os.environ.get("DFS_BASE", "https://api.dataforseo.com/v3")

# 問い合わせの直前に地域名と一緒に打たれやすい言葉。順番がそのまま表示順。
MODIFIERS = ["", "おすすめ", "費用", "相場", "料金", "口コミ", "評判", "業者", "安い", "比較"]

# 都道府県 → DataForSEO の英語表記（location_name の先頭と照合する）
PREFECTURES = {
    "北海道": "Hokkaido", "青森県": "Aomori", "岩手県": "Iwate", "宮城県": "Miyagi", "秋田県": "Akita",
    "山形県": "Yamagata", "福島県": "Fukushima", "茨城県": "Ibaraki", "栃木県": "Tochigi", "群馬県": "Gunma",
    "埼玉県": "Saitama", "千葉県": "Chiba", "東京都": "Tokyo", "神奈川県": "Kanagawa", "新潟県": "Niigata",
    "富山県": "Toyama", "石川県": "Ishikawa", "福井県": "Fukui", "山梨県": "Yamanashi", "長野県": "Nagano",
    "岐阜県": "Gifu", "静岡県": "Shizuoka", "愛知県": "Aichi", "三重県": "Mie", "滋賀県": "Shiga",
    "京都府": "Kyoto", "大阪府": "Osaka", "兵庫県": "Hyogo", "奈良県": "Nara", "和歌山県": "Wakayama",
    "鳥取県": "Tottori", "島根県": "Shimane", "岡山県": "Okayama", "広島県": "Hiroshima", "山口県": "Yamaguchi",
    "徳島県": "Tokushima", "香川県": "Kagawa", "愛媛県": "Ehime", "高知県": "Kochi", "福岡県": "Fukuoka",
    "佐賀県": "Saga", "長崎県": "Nagasaki", "熊本県": "Kumamoto", "大分県": "Oita", "宮崎県": "Miyazaki",
    "鹿児島県": "Kagoshima", "沖縄県": "Okinawa",
}

# 市名から都道府県を推定できる主な市（政令指定都市・県庁所在地など）。無ければ画面で都道府県を入れてもらう。
CITY_TO_PREF = {
    "札幌市": "北海道", "仙台市": "宮城県", "さいたま市": "埼玉県", "千葉市": "千葉県", "横浜市": "神奈川県",
    "川崎市": "神奈川県", "相模原市": "神奈川県", "新潟市": "新潟県", "静岡市": "静岡県", "浜松市": "静岡県",
    "名古屋市": "愛知県", "京都市": "京都府", "大阪市": "大阪府", "堺市": "大阪府", "神戸市": "兵庫県",
    "岡山市": "岡山県", "広島市": "広島県", "北九州市": "福岡県", "福岡市": "福岡県", "熊本市": "熊本県",
    "青森市": "青森県", "盛岡市": "岩手県", "秋田市": "秋田県", "山形市": "山形県", "福島市": "福島県",
    "水戸市": "茨城県", "宇都宮市": "栃木県", "前橋市": "群馬県", "高崎市": "群馬県", "富山市": "富山県",
    "金沢市": "石川県", "福井市": "福井県", "甲府市": "山梨県", "長野市": "長野県", "岐阜市": "岐阜県",
    "津市": "三重県", "大津市": "滋賀県", "奈良市": "奈良県", "和歌山市": "和歌山県", "鳥取市": "鳥取県",
    "松江市": "島根県", "山口市": "山口県", "徳島市": "徳島県", "高松市": "香川県", "松山市": "愛媛県",
    "高知市": "高知県", "佐賀市": "佐賀県", "長崎市": "長崎県", "大分市": "大分県", "宮崎市": "宮崎県",
    "鹿児島市": "鹿児島県", "那覇市": "沖縄県", "芦屋市": "兵庫県", "新居浜市": "愛媛県", "釧路市": "北海道",
}


def norm(s: str) -> str:
    """Google 広告は全角・大文字・空白を正規化して返すので、照合用に同じ寄せ方をする。"""
    s = (s or "").strip().lower()
    s = s.translate(str.maketrans({"　": " "}))
    return re.sub(r"\s+", " ", s)


def build_keywords(area: str, service: str, extra: list[str] | None = None) -> list[str]:
    """商談で見せる候補語を、重複なし・表示順で返す。先頭が「サービス 地域」。"""
    area, service = area.strip(), service.strip()
    out: list[str] = []

    def add(k: str) -> None:
        k = re.sub(r"\s+", " ", k.strip())
        if k and norm(k) not in {norm(x) for x in out}:
            out.append(k)

    if area and service:
        for m in MODIFIERS:
            add(f"{service} {area} {m}")
        add(f"{area} {service}")
        add(f"{area} {service} おすすめ")
    for k in extra or []:
        add(k)
    if service:
        add(service)  # 全国の目安（地域なし）
    return out


def guess_prefecture(area: str) -> str | None:
    area = area.strip()
    if area in PREFECTURES:
        return area
    for p in PREFECTURES:
        if area and p.startswith(area):  # 「千葉」「東京」など県なし表記
            return p
    for city, pref in CITY_TO_PREF.items():
        if area.startswith(city) or (area + "市") == city:
            return pref
    return None


# ---------- Google 検索候補（無料・キー不要） ----------

async def google_suggest(q: str, client: httpx.AsyncClient) -> list[str]:
    try:
        r = await client.get(
            "https://www.google.com/complete/search",
            params={"client": "firefox", "hl": "ja", "gl": "jp", "q": q},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        return [str(x) for x in data[1]] if isinstance(data, list) and len(data) > 1 else []
    except Exception:
        return []


# ---------- DataForSEO（Google 広告の検索ボリューム） ----------

def dfs_auth() -> tuple[str, str] | None:
    login, pw = os.environ.get("DATAFORSEO_LOGIN"), os.environ.get("DATAFORSEO_PASSWORD")
    return (login, pw) if login and pw else None


@dataclass
class Volume:
    kw: str
    volume: int | None = None            # 月平均（直近12か月）
    monthly: list[dict[str, Any]] = field(default_factory=list)  # [{year, month, search_volume}]
    competition: str | None = None
    cpc: float | None = None
    fetched_at: float = 0.0

    @property
    def latest(self) -> int | None:
        """直近月の数字（「今これくらい」用）。"""
        if not self.monthly:
            return None
        m = sorted(self.monthly, key=lambda x: (x.get("year", 0), x.get("month", 0)))[-1]
        return m.get("search_volume")


def parse_dfs_volumes(payload: dict[str, Any], keywords: list[str]) -> dict[str, Volume]:
    """DataForSEO の応答を {正規化キーワード: Volume} に直す。返ってこなかった語は volume=None。"""
    now = time.time()
    out = {norm(k): Volume(kw=k, fetched_at=now) for k in keywords}
    for task in payload.get("tasks") or []:
        if task.get("status_code") != 20000:
            raise RuntimeError(f"DataForSEO: {task.get('status_code')} {task.get('status_message')}")
        for item in task.get("result") or []:
            key = norm(item.get("keyword", ""))
            if key not in out:
                continue
            v = out[key]
            v.volume = item.get("search_volume")
            v.monthly = item.get("monthly_searches") or []
            v.competition = item.get("competition")
            v.cpc = item.get("cpc")
    return out


class VolumeCache:
    """(キーワード, 地域コード) ごとに結果を sqlite に取っておく。商談中の再表示を一瞬にし、API 代も節約。"""

    def __init__(self, path: Path | None = None, ttl: int = VOLUME_TTL_SEC):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.path = path or CACHE_DIR / "volumes.sqlite"
        self.ttl = ttl
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS vol (k TEXT, loc INTEGER, data TEXT, at REAL, PRIMARY KEY (k, loc))")
            c.commit()

    def _conn(self):
        return contextlib.closing(sqlite3.connect(self.path))

    def get_many(self, keywords: list[str], loc: int, now: float | None = None) -> dict[str, Volume]:
        now = now or time.time()
        found: dict[str, Volume] = {}
        with self._conn() as c:
            for k in keywords:
                row = c.execute("SELECT data, at FROM vol WHERE k=? AND loc=?", (norm(k), loc)).fetchone()
                if row and now - row[1] < self.ttl:
                    d = json.loads(row[0])
                    found[norm(k)] = Volume(**d)
        return found

    def put_many(self, vols: dict[str, Volume], loc: int) -> None:
        with self._conn() as c:
            c.executemany(
                "INSERT OR REPLACE INTO vol (k, loc, data, at) VALUES (?,?,?,?)",
                [(k, loc, json.dumps(asdict(v), ensure_ascii=False), v.fetched_at) for k, v in vols.items()],
            )
            c.commit()


async def fetch_volumes(
    keywords: list[str],
    client: httpx.AsyncClient,
    location_code: int = JAPAN,
    cache: VolumeCache | None = None,
) -> tuple[dict[str, Volume], str | None]:
    """キーワードの月間検索数を返す。戻りは ({正規化kw: Volume}, エラー文 or None)。"""
    cache = cache or VolumeCache()
    result = cache.get_many(keywords, location_code)
    missing = [k for k in keywords if norm(k) not in result]
    if not missing:
        return result, None
    auth = dfs_auth()
    if not auth:
        return result, "DataForSEO の ID/パスワードが未設定です（.env を確認）"
    body = [{
        "keywords": missing[:1000],
        "location_code": location_code,
        "language_code": "ja",
        "search_partners": False,
    }]
    try:
        r = await client.post(f"{DFS_BASE}/keywords_data/google_ads/search_volume/live", json=body, auth=auth, timeout=40)
        r.raise_for_status()
        fresh = parse_dfs_volumes(r.json(), missing)
    except Exception as e:  # 数字が出なくても候補語は見せたいので落とさない
        return result, f"検索ボリュームを取得できませんでした: {e}"
    cache.put_many(fresh, location_code)
    result.update(fresh)
    return result, None


async def prefecture_location_code(pref: str, client: httpx.AsyncClient) -> int | None:
    """都道府県名 → DataForSEO の location_code。一覧は初回に取ってファイルに残す。"""
    en = PREFECTURES.get(pref)
    if not en:
        return None
    path = CACHE_DIR / "locations_jp.json"
    locs: list[dict[str, Any]] | None = None
    if path.exists():
        try:
            locs = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            locs = None
    if locs is None:
        auth = dfs_auth()
        if not auth:
            return None
        try:
            r = await client.get(f"{DFS_BASE}/keywords_data/google_ads/locations/jp", auth=auth, timeout=40)
            r.raise_for_status()
            locs = (r.json().get("tasks") or [{}])[0].get("result") or []
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(locs, ensure_ascii=False), encoding="utf-8")
        except Exception:
            return None
    return match_prefecture(en, locs)


def match_prefecture(en: str, locs: list[dict[str, Any]]) -> int | None:
    for loc in locs:
        name = str(loc.get("location_name", ""))
        if name.split(",")[0].strip().lower() == en.lower() and str(loc.get("location_type", "")).lower() in (
            "prefecture", "region", "state", "province"
        ):
            return int(loc["location_code"])
    return None


# ---------- まとめて 1 回で返す ----------

async def lookup(area: str, service: str, extra: list[str] | None = None, pref: str | None = None,
                 cache: VolumeCache | None = None) -> dict[str, Any]:
    keywords = build_keywords(area, service, extra)
    pref = (pref or "").strip() or guess_prefecture(area)
    main_kw = keywords[0] if keywords else ""
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (search-demand)"}) as client:
        jobs: list[Any] = [
            fetch_volumes(keywords, client, JAPAN, cache),
            google_suggest(main_kw, client) if main_kw else asyncio.sleep(0, result=[]),
            google_suggest(f"{area} {service}", client) if area and service else asyncio.sleep(0, result=[]),
        ]
        loc_code = await prefecture_location_code(pref, client) if pref else None
        if loc_code and service:
            jobs.append(fetch_volumes([service.strip()], client, loc_code, cache))
        res = await asyncio.gather(*jobs)

    vols, err = res[0]
    suggest = []
    for s in list(res[1]) + list(res[2]):
        if s not in suggest:
            suggest.append(s)
    suggest_norm = {norm(s) for s in suggest}

    rows = []
    for k in keywords:
        v = vols.get(norm(k)) or Volume(kw=k)
        rows.append({
            "kw": k,
            "volume": v.volume,
            "latest": v.latest,
            "monthly": sorted(v.monthly, key=lambda x: (x.get("year", 0), x.get("month", 0)))[-12:],
            "competition": v.competition,
            "cpc": v.cpc,
            "in_suggest": norm(k) in suggest_norm,
            "is_area": bool(area) and norm(area) in norm(k),
        })
    area_rows = [r for r in rows if r["is_area"]]
    total_area = sum(r["volume"] or 0 for r in area_rows)
    main = rows[0] if rows else None

    region = None
    if loc_code:
        pv, perr = res[-1]
        v = pv.get(norm(service))
        region = {"pref": pref, "location_code": loc_code, "kw": service.strip(),
                  "volume": v.volume if v else None, "latest": v.latest if v else None,
                  "monthly": sorted(v.monthly, key=lambda x: (x.get("year", 0), x.get("month", 0)))[-12:] if v else [],
                  "error": perr}
    elif pref:
        region = {"pref": pref, "location_code": None, "kw": service.strip(), "volume": None, "latest": None,
                  "monthly": [], "error": "都道府県の地域コードを取得できませんでした"}

    return {
        "area": area, "service": service, "pref": pref,
        "ads_connected": dfs_auth() is not None,
        "error": err,
        "main": main,
        "total_area": total_area,
        "rows": rows,
        "suggest": suggest,
        "region": region,
        "source": "Google 広告のキーワードプランナーと同じデータ（DataForSEO 経由・日本・直近12か月の月平均）",
    }
