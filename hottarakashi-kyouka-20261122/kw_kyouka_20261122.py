# -*- coding: utf-8 -*-
"""ほったらかし集客の検索強化：記事のことばを在庫（media.db の keywords）に足す（2026-11-22 上野さん「全部チェックお願い」）。

  python3 kw_kyouka_20261122.py --preview                  # DB を使わず、サジェストで集まる語だけ見る（どこでも動く）
  docker exec -i mediamusou python3 - --dry < kw_kyouka_20261122.py   # 在庫と照らして、入る語を見るだけ
  docker exec -i mediamusou python3 - < kw_kyouka_20261122.py         # 入れる（priority=10・source='kyouka20261122'）
  戻すとき: DELETE FROM keywords WHERE source='kyouka20261122' AND status='new';

★lab_seeds.py と同じ決まり★ こちらが決めるのは起点の語だけ。入れるのは Google サジェストに出た語（＝実際に人が打っている語）だけ。
  他社名の語・仕事を探す人の語（バイト・副業・求人・在宅）・日本語の無い語は落とす。在庫にある語は入れない。
入れ先：
  ① ラボ（kakanai）… 申し込みに近い「代行・自動化」の語
  ② 業種の自社媒体（sougo_links.SERVICE と同じ対応）… 「業種 × 集客」の語。記事の下の枠から業種別LPへつながる
"""
import json, os, re, sqlite3, sys, time, urllib.parse, urllib.request

DB = os.environ.get("MEDIA_DB", "/data/media.db")
DRY = "--dry" in sys.argv
PREVIEW = "--preview" in sys.argv
SRC = "kyouka20261122"
UA = "Mozilla/5.0 (compatible; MusouMedia/1.0)"
SLEEP = 0.7

LAB = ("kakanai", [
    "ブログ代行", "ブログ記事作成代行", "コラム代行", "コラム記事 作成 依頼", "SEO記事 代行", "SEO記事作成代行",
    "オウンドメディア運用代行 費用", "AI記事作成ツール", "AIライティングツール", "記事 自動生成", "ブログ 自動生成",
    "ブログ 自動投稿", "WordPress 自動投稿", "集客 自動化", "Web集客 自動化", "ほったらかし 集客",
    "ブログ 毎日更新 効果", "ホームページ 記事 増やす",
])
# 業種の自社媒体 slug → 起点の語（業種別LP: build_gyoshu.py の id）
GYO = {
    "shika": ["歯科医院 集患", "歯医者 新患 増やす", "歯科医院 集客", "歯科 ホームページ 集患"],
    "kaigo": ["介護施設 集客", "デイサービス 集客", "訪問看護 集客"],
    "sougi": ["葬儀社 集客", "石材店 集客"],
    "hoken": ["保険代理店 集客", "保険 見込み客"],
    "juku": ["学習塾 集客", "塾 生徒募集", "習い事 教室 集客", "料理教室 集客"],
    "shigyo": ["社労士 集客", "司法書士 集客"],
    "biyoiryo": ["美容クリニック 集客", "美容皮膚科 集患"],
    "chiryoin": ["鍼灸院 集客"],
    "gym": ["ヨガスタジオ 集客", "ピラティス 集客"],
    "kuruma": ["中古車販売 集客", "整備工場 集客", "車検 集客"],
    "kaketsuke": ["害虫駆除 集客", "鍵屋 集客", "水道修理 集客"],
    "katazuke": ["不用品回収 集客", "遺品整理 集客", "引越し業者 集客"],
    "bridal": ["結婚相談所 集客", "結婚式場 集客"],
    "pet": ["トリミングサロン 集客", "動物病院 集客", "ペットホテル 集客"],
    "inbound": ["旅館 集客", "民泊 集客"],
    "koumuten": ["外壁塗装 集客", "建設業 ホームページ 集客"],
}
NG = re.compile(r"(?:バイト|アルバイト|副業|求人|在宅|募集中|ログイン|無料 ダウンロード|エロ|アダルト|知恵袋)")
# 自分で道具を組む人の語（API・Python・ノーコード・SNSへの転送）。サービスを探す人ではないので入れない
NG_DIY = re.compile(r"(?:\bapi\b|python|dify|zapier|make\.com|プラグイン|instagram|インスタ wordpress|\bx 自動投稿|ブログ x|wordpress x|"
                    r"\bnote\b|ホットペッパー|chatgpt|claude|gemini)", re.I)
NG_CORP = re.compile(r"(?:株式会社|有限会社|合同会社|ブランドクラウド|アテンド|ブランディングワークス|"
                     r"ウィルゲート|ナイル|PLAN-B|プランビー|ジオコード|サクラサク|ディーエムソリューションズ|ibj|"
                     r"chatgpt ?plus|jasper|catchy|ラクリン|sakubun|トランスコープ|ai-?writer|ブログ村)", re.I)
JP = re.compile(r"[ぁ-んァ-ヴ一-龥]")


def suggest(q):
    url = "https://suggestqueries.google.com/complete/search?client=firefox&hl=ja&q=" + urllib.parse.quote(q)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=12) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        return [s for s in (d[1] if len(d) > 1 else []) if isinstance(s, str)]
    except Exception:
        return []


def head(seed):
    """起点の語の頭（最初の語）。集まった語にこれが入っていないものは話がずれているので落とす。"""
    return re.split(r"[\s　]+", seed.strip())[0]


def collect(seeds):
    got = {}
    for s in seeds:
        h = head(s)
        for w in suggest(s):
            w = w.strip()
            if not (4 <= len(w) <= 40) or NG.search(w) or NG_CORP.search(w) or NG_DIY.search(w) or not JP.search(w):
                continue
            if h.lower() not in w.lower().replace(" ", "").replace("　", "") and h.lower() not in w.lower():
                continue
            got.setdefault(w, s)
        time.sleep(SLEEP)
    return got


def plan():
    out = {LAB[0]: collect(LAB[1])}
    for slug, seeds in GYO.items():
        out[slug] = collect(seeds)
    return out


def main():
    p = plan()
    if PREVIEW:
        for slug, ws in p.items():
            print(f"[{slug}] {len(ws)}語: " + " / ".join(ws))
        return
    con = sqlite3.connect(DB, timeout=60)
    total = 0
    for slug, ws in p.items():
        r = con.execute("SELECT id, name FROM sites WHERE slug=?", (slug,)).fetchone()
        if not r:
            print(f"★媒体が無いので飛ばす: {slug}")
            continue
        sid, name = r
        have = {x[0] for x in con.execute("SELECT keyword FROM keywords WHERE site_id=?", (sid,))}
        new = [w for w in ws if w not in have]
        print(f"[{slug}] {name}: 集まった{len(ws)}語・在庫に無い{len(new)}語: " + " / ".join(new))
        total += len(new)
        if not DRY and new:
            con.executemany("INSERT INTO keywords(site_id, keyword, status, priority, created_at, source)"
                            " VALUES(?,?,'new',10,datetime('now','localtime'),?)", [(sid, w, SRC) for w in new])
    if not DRY:
        con.commit()
    print(("入れた" if not DRY else "入る予定"), total, "語")
    con.close()


if __name__ == "__main__":
    main()
