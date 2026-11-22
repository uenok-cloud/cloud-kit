# -*- coding: utf-8 -*-
"""業種別LP24本を、実際に検索される言葉に合わせる（2026-11-22 上野さん「全部チェックお願い」）。

変えるのは4か所だけ。デザイン・料金・事例・申し込みの箱は触らない。
  ① <title> と og:title … 「歯科医院向けほったらかし集客｜…」→「歯科医院の集患・ブログ記事代行｜ほったらかし集客」
  ② <meta name="description"> … 頭に「業種＋集客・記事代行」と料金を入れる
  ③ 最初の見出しの小さい字 … 「記事作りは、まるごとおまかせ。」→「歯科医院の集患・ブログ記事代行は、まるごとおまかせ。」
  ④ 「よくある質問」3問（FAQPage の構造化データ付き）を「◯◯の集客を記事で学ぶ」の手前に1つ足す
     <!--kyouka:start-->〜<!--kyouka:end--> の間だけ。何度流しても同じ所が置き換わるだけ
使い方（lp_sougo.py と同じ）:
  python3 lp_kensaku_kyouka.py --root /opt/salesfeed/portal/kakanai            # 変わる所を見るだけ
  python3 lp_kensaku_kyouka.py --root /opt/salesfeed/portal/kakanai --write    # 書き込む（元は index.html.bak-kyouka-日付）
  戻すとき: 各 <id>/index.html.bak-kyouka-日付 を index.html に戻す
目印が想定どおりに無いページは、黙って進まずに飛ばして名前を出す。
"""
import argparse, datetime, html, json, os, re, shutil, sys

# id: (新しい題名の頭, 読み手, 呼び名, 書き方の約束)  読み手・呼び名・約束は build_gyoshu.py の GYOSHU と同じ
SEO = {
 "shika": ("歯科医院の集患・ブログ記事代行", "歯科医院", "医院", "医療広告ガイドラインに合わせて書きます。自費診療の記事には、費用・治療期間・主なリスクをあわせて書きます。体験談やビフォーアフターは使いません。"),
 "clinic": ("クリニックの集患・ブログ記事代行", "クリニック・医院", "医院", "医療広告ガイドラインに合わせて書きます。体験談やビフォーアフター、「最高」などの比較表現は使いません。記事は、症状の一般的な解説と受診の目安にとどめます。"),
 "biyoiryo": ("美容クリニックの集客・コラム記事代行", "美容クリニック", "クリニック", "医療広告ガイドラインに合わせて書きます。体験談・ビフォーアフター・「必ず」「最高」などの表現は使いません。自由診療の記事には、費用・期間・主なリスクや副作用をあわせて書きます。"),
 "chiryoin": ("整骨院・整体院の集客・ブログ代行", "整骨院・整体院・鍼灸院", "院", "あん摩マッサージ指圧師・はり師・きゅう師、柔道整復師の広告の決まりと、景品表示法に合わせて書きます。「治る」「効く」と言い切る表現や体験談は使いません。"),
 "kaigo": ("介護施設・事業所の集客と記事代行", "介護・福祉の事業所", "事業所", "利用者さまの個人情報や写真は出しません。「必ず採用できる」などの表現は使いません。"),
 "fudosan": ("不動産会社の集客・ブログ記事代行", "不動産会社", "会社", "不動産の表示に関する公正競争規約に合わせて書きます。「必ず高く売れる」「最高値」などの表現は使いません。"),
 "kensetsu": ("工務店・建設会社の集客・記事代行", "建設会社・工務店", "会社", "「地域No.1」「最安」など、根拠のない表現は使いません。"),
 "inshoku": ("飲食店の集客・ブログ記事代行", "飲食店", "お店", "「地域で一番」「絶対においしい」など、根拠のない表現は使いません。"),
 "tenpo": ("店舗・サロンの集客・ブログ代行", "美容室・サロン・お店", "お店", "薬機法に合わせ、化粧品や施術の効果を言い切る表現は使いません。"),
 "yado": ("旅館・ホテルの集客・記事代行", "旅館・ホテル", "宿", "「日本一」「最安」など、根拠のない表現は使いません。"),
 "houjin": ("BtoB企業のオウンドメディア記事代行", "法人向けサービスの会社", "会社", "ほかの会社を名指しで比べる書き方はしません。"),
 "netshop": ("ネットショップの集客・記事代行", "ネットショップ", "お店", "景品表示法に合わせ、「No.1」「最安」など根拠のない表現は使いません。化粧品や健康食品は、効果を言い切る書き方をしません。"),
 "gym": ("ジム・ヨガスタジオの集客・記事代行", "ジム・ヨガスタジオ", "ジム", "景品表示法に合わせ、「必ず痩せる」のように効果を約束する表現や、根拠のない数字は使いません。"),
 "juku": ("学習塾・教室の生徒募集・記事代行", "学習塾・スクール・教室", "教室", "合格実績は、年度と人数を添えた事実だけを書きます。「成績が必ず上がる」などの表現は使いません。"),
 "shigyo": ("税理士・士業事務所の集客・コラム代行", "士業の事務所", "事務所", "各士業会の広告に関する規程に合わせて書きます。誇大な表現や、ほかの事務所との比較はしません。"),
 "houritsu": ("法律事務所の集客・コラム記事代行", "法律事務所", "事務所", "弁護士等の業務広告に関する規程に合わせて書きます。「必ず勝てる」などの表現や、ほかの事務所との比較はしません。"),
 "hoken": ("保険代理店の集客・記事代行", "保険代理店・FP", "会社", "保険業法と、所属する保険会社の広告のルールに合わせて書きます。「必ず得する」などの表現は使いません。"),
 "sougi": ("葬儀社・石材店の集客・記事代行", "葬儀社・石材店", "会社", "不安をあおる書き方（「今すぐ決めないと損」など）はしません。費用は、内訳と条件を添えて書きます。"),
 "kaitori": ("買取店の集客・ブログ記事代行", "買取店・リユース店", "お店", "古物営業法と景品表示法に合わせて書きます。「どこよりも高く」「最高値」など根拠のない表現は使いません。"),
 "kuruma": ("車屋・整備工場の集客・記事代行", "中古車販売店・整備工場", "お店", "自動車公正競争規約（クルマの表示の決まり）に合わせて書きます。「地域最安」など根拠のない表現は使いません。"),
 "kaketsuke": ("便利屋・害虫駆除の集客・記事代行", "出張修理・駆除の会社", "会社", "料金は、作業の内容と条件を添えて書きます。「業界最安」など根拠のない表現や、不安をあおる書き方はしません。"),
 "katazuke": ("不用品回収・引っ越しの集客・記事代行", "片付け・引っ越しの会社", "会社", "許可の内容を偽る表現や、「最安」など根拠のない表現は使いません。"),
 "bridal": ("結婚式場・写真館の集客・記事代行", "ブライダル・写真館", "会社", "「成婚率No.1」「最安」など根拠のない表現は使いません。料金は、含まれるものと条件を添えて書きます。"),
 "pet": ("ペットサロン・動物病院の集客・記事代行", "動物病院・ペットサロン", "お店", "動物病院の記事は、獣医療の広告の決まりに合わせて書きます。病気の診断や治療を言い切る表現は使いません。"),
}
BRAND = "ほったらかし集客"
H1_OLD = "<h1><small>記事作りは、まるごとおまかせ。</small>"
MARK_S, MARK_E = "<!--kyouka:start-->", "<!--kyouka:end-->"


def faq(seo, who, unit, yaku):
    qa = [
        (f"{who}のブログやコラムの記事も、代行してもらえますか？",
         f"はい。{who}のお客さんが実際に検索している言葉を調べ、その答えになる記事を毎日2本（月60本）、{unit}のホームページに公開します。書き方の約束：{yaku}"),
        (f"記事を書く時間がなくても、{who}の集客に使えますか？",
         f"使えます。言葉の調査から、記事の作成・点検・公開・手直しまでこちらで行います。{unit}側の作業は、月30分ほどの確認だけです。検索の順位や売上をお約束するものではありません。"),
        ("費用はいくらですか？",
         f"1年プランは月29,800円（税抜・1日あたり約993円）、半年プランは月39,800円、3ヶ月プランは月59,800円です。申し込む前に、{unit}の記事を1本、無料でお作りできます。"),
    ]
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
    dl = "".join(f'<dt style="font-weight:700;margin:18px 0 6px">Q. {html.escape(q)}</dt><dd style="margin:0">{html.escape(a)}</dd>' for q, a in qa)
    return (f'{MARK_S}<section data-kyouka="20261122"><div class="in" style="overflow-wrap:anywhere">'
            f'<h2>{html.escape(seo)}のよくある質問</h2><div class="rule"></div>'
            f'<dl style="text-align:left;line-height:1.8;margin:14px 0">{dl}</dl>'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
            f'</div></section>{MARK_E}')


def patch(s, gid):
    seo, who, unit, yaku = SEO[gid]
    title = f"{seo}｜{BRAND}"
    desc = (f"{seo}なら{BRAND}。{who}のお客さんが検索する言葉を調べ、答えになる記事を毎日2本、{unit}のホームページに公開します。"
            f"1日993円（税抜）から。{unit}の名前とメールを入れるだけで、記事を1本無料でお作りします。")
    errs = []
    s2, n = re.subn(r"<title>[^<]*</title>", f"<title>{html.escape(title)}</title>", s, count=1)
    if n != 1: errs.append("title")
    s2, n = re.subn(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(title)}">', s2, count=1)
    if n != 1: errs.append("og:title")
    s2, n = re.subn(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc)}">', s2, count=1)
    if n != 1: errs.append("description")
    new_h1 = f"<h1><small>{html.escape(seo)}は、まるごとおまかせ。</small>"
    if s2.count(H1_OLD) == 1:
        s2 = s2.replace(H1_OLD, new_h1)
    elif s2.count(new_h1) != 1:
        errs.append("h1")
    block = faq(seo, who, unit, yaku)
    if MARK_S in s2:
        s2 = re.sub(re.escape(MARK_S) + ".*?" + re.escape(MARK_E), lambda m: block, s2, count=1, flags=re.S)
    elif s2.count("<!--sougo:start-->") == 1:
        s2 = s2.replace("<!--sougo:start-->", block + "\n<!--sougo:start-->")
    elif s2.count('<section class="last">') == 1:
        s2 = s2.replace('<section class="last">', block + '\n<section class="last">')
    else:
        errs.append("faqの差し込み先")
    return s2, title, desc, errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    stamp = datetime.date.today().strftime("%Y%m%d")
    done = 0
    for gid in (a.ids or SEO):
        p = os.path.join(a.root, gid, "index.html")
        if not os.path.exists(p):
            print(f"★ページが無い {gid}"); continue
        s = open(p, encoding="utf-8").read()
        s2, title, desc, errs = patch(s, gid)
        if errs:
            print(f"★目印が合わないので飛ばす {gid}: {', '.join(errs)}"); continue
        print(f"{gid}: {title}\n    {desc}")
        if a.write and s2 != s:
            bk = p + ".bak-kyouka-" + stamp
            if not os.path.exists(bk):
                shutil.copy2(p, bk)
            open(p, "w", encoding="utf-8").write(s2)
            done += 1
    print(("書き込んだ" if a.write else "変わる予定（--write で書き込み）"), done if a.write else len(a.ids or SEO), "ページ")


if __name__ == "__main__":
    main()
