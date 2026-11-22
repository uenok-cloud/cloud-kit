# -*- coding: utf-8 -*-
"""業種別のほったらかし集客LPを作る。土台は ../ad/index.html（広告用の短いLP）。
使い方: python3 build_gyoshu.py  →  gyoshu/<id>/index.html
業種を足すときは GYOSHU に1つ足すだけ。土台の文言が変わって目印が外れたら、黙って進まずに止まる。
約束: お客さまの数字は実測だけ（他業種の数字は他業種と書く）／その業種の事例が無いうちは「まだありません」と書く／
順位・売上を約束しない／業種ごとの広告の決まりを「書き方の約束」に入れる。"""
import pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent / "ad" / "index.html"

# unit=読み手の呼び名（会社/お店/事業所/宿） your=絵の中の言い方 ask=業種の聞き方 goal=記事を読んだ人が進む先
# media=このLPへつなぐ媒体(sites.slug)。case_same=True は、載せている事例が同じ業種のとき（「まだありません」を出さない）
GYOSHU = [
 {"id": "fudosan", "label": "不動産向け", "who": "不動産会社", "gyo": "不動産業", "media": ["fudosan"],
  "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の問い合わせページに来ます。",
  "ink": "#13294B", "sun": "#7CC6FF", "lemon": "#DCEBFA", "ground": "#F3F8FD", "sub": "#4d5a6b", "line": "#d5e0ec",
  "ribbon": "売却の相談が、<b>ポータルサイト頼み</b>なら。",
  "target": "家を売りたい人に、",
  "search": "家を売りたい人や、相続した家に悩む人が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["売却の相談が、ポータルサイト頼みになっている", "反響1件あたりの費用が上がっている"],
  "articles": ["相続した実家を売るときの手順と税金の基本", "住み替えは、売るのが先？買うのが先？", "空き家をそのままにしておくと起きること"],
  "yaku": "不動産の表示に関する公正競争規約に合わせて書きます。「必ず高く売れる」「最高値」などの表現は使いません。",
  "ph_co": "◯◯不動産", "ph_gy": "不動産の売買仲介", "ph_ar": "大阪府吹田市"},
 {"id": "kensetsu", "label": "建設・建築向け", "who": "建設会社・工務店", "gyo": "建設・建築業", "media": ["nyusatsu"],
  "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の問い合わせページに来ます。",
  "ink": "#231F1A", "sun": "#FF9A3D", "lemon": "#FFE4C7", "ground": "#FFF7EE", "sub": "#5c5347", "line": "#eadccb",
  "ribbon": "相見積もりが、<b>価格だけ</b>の勝負なら。",
  "target": "家を建てる人・直す人に、",
  "search": "家を建てたい人や、リフォーム・修理を考えている人が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["紹介サイトの手数料や広告費が高い", "相見積もりで、価格だけの勝負になる"],
  "articles": ["外壁塗装の費用相場と、見積もりで見るべき3か所", "キッチンリフォームでよくある失敗", "雨漏りの原因と、応急処置でやってはいけないこと"],
  "yaku": "「地域No.1」「最安」など、根拠のない表現は使いません。",
  "ph_co": "◯◯工務店", "ph_gy": "注文住宅・リフォーム", "ph_ar": "愛知県岡崎市"},
 {"id": "kaigo", "label": "介護・福祉向け", "who": "介護・福祉の事業所", "gyo": "介護・福祉", "media": ["kaigo"],
  "unit": "事業所", "your": "事業所", "ask": "何の事業所", "goal": "そのまま事業所の問い合わせページに来ます。",
  "ink": "#24361B", "sun": "#A8E06A", "lemon": "#E3F5CF", "ground": "#F6FBEF", "sub": "#525e49", "line": "#dbe7cd",
  "ribbon": "応募が、<b>求人広告頼み</b>なら。",
  "target": "施設や仕事を探す人に、",
  "search": "介護の仕事を探している人や、ご家族の施設を探している人が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["人が採れず、求人広告費がかさむ", "利用者のご家族に、事業所の雰囲気が伝わらない"],
  "articles": ["訪問看護の1日の流れ（はじめての方へ）", "未経験から介護職へ。最初の3か月で覚えること", "デイサービスの見学で確認したい5つのこと"],
  "yaku": "利用者さまの個人情報や写真は出しません。「必ず採用できる」などの表現は使いません。",
  "ph_co": "◯◯デイサービス", "ph_gy": "通所介護（デイサービス）", "ph_ar": "埼玉県川越市"},
 {"id": "inshoku", "label": "飲食店向け", "who": "飲食店", "gyo": "飲食店", "media": ["gohan"],
  "unit": "お店", "your": "お店", "ask": "何のお店", "goal": "そのままお店や問い合わせページに来ます。",
  "ink": "#2B1A14", "sun": "#FF7B6B", "lemon": "#FFDDD6", "ground": "#FFF5F2", "sub": "#5e4d47", "line": "#efd9d3",
  "ribbon": "集客が、<b>グルメサイト頼み</b>なら。",
  "target": "お店を探している人に、",
  "search": "近くで食事のお店を探している人が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["グルメサイトの掲載料や手数料が重い", "新しいお客さんが、口コミと通りがかりに頼っている"],
  "articles": ["歓送迎会のお店選びで、幹事が確認したい5つのこと", "子連れで入りやすいお店の見分け方", "テイクアウトをおいしく食べるための持ち帰り方"],
  "yaku": "「地域で一番」「絶対においしい」など、根拠のない表現は使いません。",
  "ph_co": "◯◯食堂", "ph_gy": "イタリアンレストラン", "ph_ar": "福岡県久留米市"},
 {"id": "tenpo", "label": "店舗・サロン向け", "who": "美容室・サロン・お店", "gyo": "美容室・サロン", "media": ["meo"],
  "unit": "お店", "your": "お店", "ask": "何のお店", "goal": "そのままお店や問い合わせページに来ます。",
  "ink": "#2A1B2E", "sun": "#FF9EC4", "lemon": "#FFDCEB", "ground": "#FFF5F9", "sub": "#5b4d5c", "line": "#eed8e3",
  "ribbon": "新規の予約が、<b>予約サイト頼み</b>なら。",
  "target": "近くのお店を探す人に、",
  "search": "髪や肌の悩みを調べている人や、近くのお店を探している人が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["予約サイトの手数料と、価格の競争がつらい", "リピートは来るのに、新しいお客様が増えない"],
  "articles": ["髪のパサつき、シャンプーより先に見直すこと", "まつ毛パーマを長持ちさせる毎日のケア", "ブライダルエステはいつから始める？"],
  "yaku": "薬機法に合わせ、化粧品や施術の効果を言い切る表現は使いません。",
  "ph_co": "◯◯ヘアサロン", "ph_gy": "美容室", "ph_ar": "神奈川県藤沢市"},
 {"id": "yado", "label": "宿・ホテル向け", "who": "旅館・ホテル", "gyo": "宿泊業", "media": ["inbound"],
  "unit": "宿", "your": "宿", "ask": "どんな宿", "goal": "そのまま宿の予約や問い合わせのページに来ます。",
  "ink": "#2A2140", "sun": "#C3A6FF", "lemon": "#E6DBFF", "ground": "#F8F5FF", "sub": "#544d63", "line": "#ddd5ec",
  "ribbon": "予約が、<b>予約サイト頼み</b>なら。",
  "target": "旅先の宿を探す人に、",
  "search": "旅行の行き先や、泊まる宿を探している人が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["予約サイトの手数料が重い", "自分のホームページからの予約が増えない"],
  "articles": ["子連れの温泉旅行で、宿に確認しておきたいこと", "雨の日でも楽しめる、宿のまわりの過ごし方", "はじめての一人旅、宿選びで見るところ"],
  "yaku": "「日本一」「最安」など、根拠のない表現は使いません。",
  "ph_co": "◯◯旅館", "ph_gy": "温泉旅館", "ph_ar": "大分県由布市"},
 {"id": "houjin", "label": "法人向け", "who": "法人向けサービスの会社", "gyo": "法人向けサービス", "case_same": True,
  "media": ["teleapo", "jinmyaku", "kokoku", "yushi", "zeikin", "shokei", "chizai"],
  "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の問い合わせページに来ます。",
  "ink": "#142A2E", "sun": "#5FD6C8", "lemon": "#D2F1ED", "ground": "#F1FAF9", "sub": "#4a5b5d", "line": "#d2e4e2",
  "ribbon": "仕事が、<b>紹介頼み</b>になっているなら。",
  "target": "外注先を探す担当者に、",
  "search": "外注先や取引先を探している法人の担当者が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["仕事が、紹介と既存のお客様だけに頼っている", "専門性を伝える記事や資料が足りない"],
  "articles": ["業務システムを外注するときの、見積もりの読み方", "営業代行を頼む前に、社内で決めておくこと", "採用サイトを作り直したほうがいいサイン"],
  "yaku": "ほかの会社を名指しで比べる書き方はしません。",
  "ph_co": "◯◯株式会社", "ph_gy": "営業代行", "ph_ar": "東京都千代田区"},
 {"id": "netshop", "label": "ネットショップ向け", "who": "ネットショップ", "gyo": "ネットショップ", "media": [],
  "unit": "お店", "your": "お店", "ask": "何のお店", "goal": "そのままお店の商品ページに来ます。",
  "ink": "#1F2616", "sun": "#D9F23E", "lemon": "#F0F8C2", "ground": "#FAFDEC", "sub": "#535a45", "line": "#e1e8c6",
  "ribbon": "売上が、<b>広告とモール頼み</b>なら。",
  "target": "商品を探している人に、",
  "search": "商品を探している人や、選び方を調べている人が、実際に検索しているワードを、こちらで調査します。",
  "pains": ["広告費とモールの手数料で、利益が残りにくい", "自分のショップに、検索から人が来ない"],
  "articles": ["A4が入る通勤バッグの選び方と、見ておきたい3か所", "革の財布を長く使うための、毎日のお手入れ", "贈り物に迷ったときの、予算別の選び方"],
  "yaku": "景品表示法に合わせ、「No.1」「最安」など根拠のない表現は使いません。化粧品や健康食品は、効果を言い切る書き方をしません。",
  "ph_co": "◯◯ストア", "ph_gy": "革小物の通販", "ph_ar": "東京都台東区"},
 # ── 2026-10-05 追加：ネット集客が広告・ポータル頼みになりやすい業態 16（媒体は media-musou/kyouka/new_media_20261005.py）
 {"id": "clinic", "label": "クリニック向け", "who": "クリニック・医院", "gyo": "クリニック・医院", "media": ["clinic"], "unit": "医院", "your": "医院", "ask": "何科の医院", "goal": "そのまま医院の予約や問い合わせのページに来ます。", "ink": "#12332B", "sun": "#7FE3B5", "lemon": "#D5F6E5", "ground": "#F2FBF6", "sub": "#4a5c54", "line": "#d3e6dc", "ribbon": "新しい患者さんが、<b>広告とポータル頼み</b>なら。", "target": "症状を調べている人に、", "search": "症状や検査のことを調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["新しい患者さんが、口コミと看板と広告に頼っている", "ホームページが、開院したときのままになっている"], "articles": ["長引く咳は何科へ？受診の目安", "健康診断で「要再検査」と言われたら", "子どもの発熱、夜間に受診したほうがいいサイン"], "yaku": "医療広告ガイドラインに合わせて書きます。体験談やビフォーアフター、「最高」などの比較表現は使いません。記事は、症状の一般的な解説と受診の目安にとどめます。", "ph_co": "◯◯内科クリニック", "ph_gy": "内科・小児科", "ph_ar": "千葉県船橋市"},
 {"id": "shika", "label": "歯科医院向け", "who": "歯科医院", "gyo": "歯科医院", "media": ["shika"], "unit": "医院", "your": "医院", "ask": "どんな歯科医院", "goal": "そのまま医院の予約や問い合わせのページに来ます。", "ink": "#0E2F44", "sun": "#5CC8F0", "lemon": "#D3EEFA", "ground": "#F1F9FD", "sub": "#4a5a66", "line": "#d2e2ec", "ribbon": "自費診療の相談が、<b>広告頼み</b>なら。", "target": "治療を調べている人に、", "search": "矯正やインプラントなど、治療の違いや費用を調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["自費診療の相談が増えない", "価格だけで比べられてしまう"], "articles": ["インプラントとブリッジ、何が違う？", "マウスピース矯正が向いている人・向いていない人", "ホワイトニングの効果はどれくらい続く？"], "yaku": "医療広告ガイドラインに合わせて書きます。自費診療の記事には、費用・治療期間・主なリスクをあわせて書きます。体験談やビフォーアフターは使いません。", "ph_co": "◯◯歯科医院", "ph_gy": "歯科（矯正・インプラント）", "ph_ar": "兵庫県西宮市"},
 {"id": "biyoiryo", "label": "美容クリニック向け", "who": "美容クリニック", "gyo": "美容クリニック", "media": ["biyoiryo"], "unit": "クリニック", "your": "クリニック", "ask": "どんなクリニック", "goal": "そのままクリニックの予約や問い合わせのページに来ます。", "ink": "#33261C", "sun": "#E8C39E", "lemon": "#F6E7D6", "ground": "#FCF7F1", "sub": "#62564b", "line": "#eadfd2", "ribbon": "予約が、<b>広告とポータル頼み</b>なら。", "target": "施術を調べている人に、", "search": "施術の違いやダウンタイム、費用を調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["広告費が上がって、予約1件にかかる費用が重い", "価格の安さだけで比べられてしまう"], "articles": ["医療脱毛とサロン脱毛、何が違う？", "シミ取りの施術、ダウンタイムの目安と過ごし方", "はじめての美容クリニック、カウンセリングで確認したいこと"], "yaku": "医療広告ガイドラインに合わせて書きます。体験談・ビフォーアフター・「必ず」「最高」などの表現は使いません。自由診療の記事には、費用・期間・主なリスクや副作用をあわせて書きます。", "ph_co": "◯◯美容クリニック", "ph_gy": "美容皮膚科", "ph_ar": "愛知県名古屋市"},
 {"id": "chiryoin", "label": "整骨院・整体院向け", "who": "整骨院・整体院・鍼灸院", "gyo": "整骨院・整体院", "media": ["chiryoin"], "unit": "院", "your": "院", "ask": "どんな院", "goal": "そのまま院の予約や問い合わせのページに来ます。", "ink": "#1C2A4A", "sun": "#F5B83D", "lemon": "#FCE9BD", "ground": "#FEF9EC", "sub": "#525a6b", "line": "#e9e0c8", "ribbon": "新規の予約が、<b>予約サイトと広告頼み</b>なら。", "target": "からだの不調を調べている人に、", "search": "肩こりや腰の痛みなど、からだの不調を調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["予約サイトの掲載料と、価格の競争がつらい", "通ってくれる方は多いのに、新しい方が増えない"], "articles": ["デスクワークの肩こり、自分でできる毎日のケア", "ぎっくり腰になった直後に、やってはいけないこと", "整骨院と整体院、何が違う？"], "yaku": "あん摩マッサージ指圧師・はり師・きゅう師、柔道整復師の広告の決まりと、景品表示法に合わせて書きます。「治る」「効く」と言い切る表現や体験談は使いません。強い痛みやしびれには、医療機関の受診をすすめる書き方にします。", "ph_co": "◯◯整骨院", "ph_gy": "整骨院・整体", "ph_ar": "埼玉県所沢市"},
 {"id": "gym", "label": "ジム・スタジオ向け", "who": "ジム・ヨガスタジオ", "gyo": "ジム・スタジオ", "media": ["gym"], "unit": "ジム", "your": "ジム", "ask": "どんなジム", "goal": "そのままジムの体験申し込みや問い合わせのページに来ます。", "ink": "#0D2B2E", "sun": "#2ED3D9", "lemon": "#C9F3F5", "ground": "#EFFBFC", "sub": "#48595b", "line": "#cfe5e6", "ribbon": "体験の申し込みが、<b>広告頼み</b>なら。", "target": "運動を始めたい人に、", "search": "運動や食事のことを調べている人や、通える場所を探している人が、実際に検索しているワードを、こちらで調査します。", "pains": ["広告を止めると、体験の申し込みも止まる", "大手や低価格のジムと、月額だけで比べられる"], "articles": ["運動が苦手な人の、最初の1か月の過ごし方", "パーソナルジムの体験で確認したい5つのこと", "筋トレは、週に何回から始める？"], "yaku": "景品表示法に合わせ、「必ず痩せる」のように効果を約束する表現や、根拠のない数字は使いません。", "ph_co": "◯◯パーソナルジム", "ph_gy": "パーソナルトレーニングジム", "ph_ar": "東京都世田谷区"},
 {"id": "juku", "label": "塾・スクール向け", "who": "学習塾・スクール・教室", "gyo": "学習塾・スクール", "media": ["juku"], "unit": "教室", "your": "教室", "ask": "何の教室", "goal": "そのまま教室の体験申し込みや問い合わせのページに来ます。", "ink": "#1B2A5C", "sun": "#FFC53D", "lemon": "#FFEBB8", "ground": "#FFFAEB", "sub": "#535a70", "line": "#ebe2c6", "ribbon": "入会の問い合わせが、<b>チラシと広告頼み</b>なら。", "target": "塾や教室を探す人に、", "search": "お子さんの勉強のことを調べている保護者や、習い事を探している人が、実際に検索しているワードを、こちらで調査します。", "pains": ["入会の問い合わせが、春と夏にかたよる", "チラシや広告の反応が落ちている"], "articles": ["中1の数学でつまずきやすい単元と、家でできる声かけ", "英検5級に向けて、家庭でできる毎日10分の練習", "塾の体験授業で見ておきたいこと"], "yaku": "合格実績は、年度と人数を添えた事実だけを書きます。「成績が必ず上がる」などの表現は使いません。", "ph_co": "◯◯進学教室", "ph_gy": "学習塾（小・中学生）", "ph_ar": "静岡県浜松市"},
 {"id": "shigyo", "label": "士業向け", "who": "士業の事務所", "gyo": "士業", "media": ["shigyo"], "unit": "事務所", "your": "事務所", "ask": "何の事務所", "goal": "そのまま事務所の問い合わせページに来ます。", "ink": "#1E3A2F", "sun": "#C9B26A", "lemon": "#EEE6C8", "ground": "#FAF8EE", "sub": "#525e56", "line": "#e3dfc8", "ribbon": "新しいご相談が、<b>紹介頼み</b>なら。", "target": "手続きで困っている人に、", "search": "手続きや制度のことで困っている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["紹介は来るが、新しいお客様の数が読めない", "専門分野や強みが、外から見えていない"], "articles": ["インボイス制度、個人事業主がまず確認すること", "会社設立の手続き、自分でやる場合と頼む場合の違い", "助成金の申請前に整えておきたい就業規則"], "yaku": "各士業会の広告に関する規程に合わせて書きます。誇大な表現や、ほかの事務所との比較はしません。個別の判断が必要な内容は書かず、「ご相談ください」とします。", "ph_co": "◯◯税理士事務所", "ph_gy": "税理士事務所", "ph_ar": "広島県福山市"},
 {"id": "houritsu", "label": "法律事務所向け", "who": "法律事務所", "gyo": "法律事務所", "media": ["houritsu"], "unit": "事務所", "your": "事務所", "ask": "どんな事務所", "goal": "そのまま事務所の相談予約や問い合わせのページに来ます。", "ink": "#3B1A22", "sun": "#D9A066", "lemon": "#F4E0CB", "ground": "#FCF6F0", "sub": "#63505a", "line": "#ead9cc", "ribbon": "ご相談が、<b>広告とポータル頼み</b>なら。", "target": "法律の悩みを調べている人に、", "search": "相続・離婚・交通事故など、法律の悩みを調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["検索広告の費用が、年々重くなっている", "ポータルサイトの中で、ほかの事務所と横並びになる"], "articles": ["相続の話し合いがまとまらないときの、進め方の基本", "交通事故にあったら、最初の1週間でしておくこと", "離婚を考えたとき、先に整理しておきたいこと"], "yaku": "弁護士等の業務広告に関する規程に合わせて書きます。「必ず勝てる」などの表現や、ほかの事務所との比較はしません。個別の見通しは書かず、「ご相談ください」とします。", "ph_co": "◯◯法律事務所", "ph_gy": "法律事務所（相続・離婚）", "ph_ar": "宮城県仙台市"},
 {"id": "hoken", "label": "保険代理店向け", "who": "保険代理店・FP", "gyo": "保険代理店", "media": ["hoken"], "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の相談予約や問い合わせのページに来ます。", "ink": "#173B5C", "sun": "#8ED081", "lemon": "#DDF2D8", "ground": "#F4FBF2", "sub": "#4c5b68", "line": "#d5e6d1", "ribbon": "ご相談が、<b>紹介と比較サイト頼み</b>なら。", "target": "お金のことを調べている人に、", "search": "保険の見直しや、家計・老後のお金のことを調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["紹介と、既存のご契約者だけに頼っている", "相談の前に、比較サイトで決まってしまう"], "articles": ["子どもが生まれたら見直したい、保険の考え方", "iDeCoとNISA、どちらから始める？", "親の介護が始まる前に確認したいお金のこと"], "yaku": "保険業法と、所属する保険会社の広告のルールに合わせて書きます。特定の商品をすすめる記事は、事前に確認を取ります。「必ず得する」などの表現は使いません。", "ph_co": "◯◯保険事務所", "ph_gy": "保険代理店", "ph_ar": "新潟県長岡市"},
 {"id": "sougi", "label": "葬儀社・石材店向け", "who": "葬儀社・石材店", "gyo": "葬儀・石材", "media": ["sougi"], "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の問い合わせページに来ます。", "ink": "#2B2A33", "sun": "#B9B4D6", "lemon": "#E6E3F2", "ground": "#F7F6FB", "sub": "#56555f", "line": "#dedce8", "ribbon": "ご相談が、<b>紹介サイト頼み</b>なら。", "target": "葬儀やお墓を調べている人に、", "search": "葬儀やお墓のことを、必要になって調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["紹介サイトの手数料が重い", "考え方や人柄が、事前に伝わらない"], "articles": ["家族葬の費用の内訳と、見積もりで確認したいこと", "墓じまいの流れと、かかる期間", "喪主がはじめにすること（当日までの流れ）"], "yaku": "不安をあおる書き方（「今すぐ決めないと損」など）はしません。費用は、内訳と条件を添えて書きます。", "ph_co": "◯◯葬祭", "ph_gy": "葬儀社（家族葬）", "ph_ar": "茨城県水戸市"},
 {"id": "kaitori", "label": "買取店向け", "who": "買取店・リユース店", "gyo": "買取・リユース", "media": ["kaitori"], "unit": "お店", "your": "お店", "ask": "何のお店", "goal": "そのままお店の査定申し込みや問い合わせのページに来ます。", "ink": "#241C0F", "sun": "#F2C230", "lemon": "#FBEBB5", "ground": "#FEFAEA", "sub": "#5c5546", "line": "#eae2c4", "ribbon": "査定の申し込みが、<b>広告と一括査定頼み</b>なら。", "target": "売りたい物がある人に、", "search": "手放したい物の売り方や、査定のことを調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["広告を止めると、査定の申し込みも止まる", "一括査定で、金額だけの勝負になる"], "articles": ["ブランドバッグを売る前に、そろえておきたい付属品", "遺品の着物、買取に出す前に確認したいこと", "出張買取と店頭買取、どちらが向いている？"], "yaku": "古物営業法と景品表示法に合わせて書きます。「どこよりも高く」「最高値」など根拠のない表現は使いません。買取の金額はお約束しません。", "ph_co": "◯◯買取センター", "ph_gy": "ブランド品・貴金属の買取", "ph_ar": "岡山県倉敷市"},
 {"id": "kuruma", "label": "自動車販売・整備向け", "who": "中古車販売店・整備工場", "gyo": "自動車販売・整備", "media": ["kuruma"], "unit": "お店", "your": "お店", "ask": "何のお店", "goal": "そのままお店の来店予約や問い合わせのページに来ます。", "ink": "#14213D", "sun": "#FF6B6B", "lemon": "#FFD9D9", "ground": "#FFF5F5", "sub": "#4e566a", "line": "#efd6d6", "ribbon": "来店が、<b>ポータルサイト頼み</b>なら。", "target": "クルマのことを調べている人に、", "search": "クルマの買い替えや車検、修理のことを調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["ポータルサイトの掲載料が重い", "車両の値段だけで比べられてしまう"], "articles": ["車検の見積もりで、見ておきたい3か所", "中古車を買うとき、走行距離より先に見るところ", "ぶつけてしまったとき、修理に出す前に確認すること"], "yaku": "自動車公正競争規約（クルマの表示の決まり）に合わせて書きます。「地域最安」など根拠のない表現は使いません。", "ph_co": "◯◯モータース", "ph_gy": "中古車販売・車検", "ph_ar": "群馬県高崎市"},
 {"id": "kaketsuke", "label": "出張修理・駆除向け", "who": "出張修理・駆除の会社", "gyo": "出張修理・駆除", "media": ["kaketsuke"], "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の問い合わせページに来ます。", "ink": "#2A1A12", "sun": "#FF8552", "lemon": "#FFDCCB", "ground": "#FFF6F1", "sub": "#5f4f47", "line": "#efd9cd", "ribbon": "仕事の依頼が、<b>検索広告頼み</b>なら。", "target": "急なトラブルで調べている人に、", "search": "水もれや鍵のトラブル、害虫のことを調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["検索広告の1クリックが高く、利益が残りにくい", "紹介サイトの手数料が重い"], "articles": ["トイレがつまったとき、自分でやってよいこと・だめなこと", "鍵をなくしたとき、業者を呼ぶ前に確認すること", "ハチの巣を見つけたら、近づく前に知っておきたいこと"], "yaku": "料金は、作業の内容と条件を添えて書きます。「業界最安」など根拠のない表現や、不安をあおる書き方はしません。", "ph_co": "◯◯設備", "ph_gy": "水まわりの修理", "ph_ar": "福岡県北九州市"},
 {"id": "katazuke", "label": "片付け・引っ越し向け", "who": "片付け・引っ越しの会社", "gyo": "片付け・引っ越し", "media": ["katazuke"], "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の見積もりや問い合わせのページに来ます。", "ink": "#1D3124", "sun": "#6DD47E", "lemon": "#D4F3D9", "ground": "#F2FBF4", "sub": "#4f5c53", "line": "#d3e6d7", "ribbon": "見積もりの依頼が、<b>一括見積もり頼み</b>なら。", "target": "片付けを調べている人に、", "search": "実家の片付けや引っ越し、不用品の出し方を調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["一括見積もりで、金額だけの勝負になる", "紹介の手数料と広告費で、利益が残りにくい"], "articles": ["実家の片付け、何から始める？", "遺品整理を頼む前に、家族で決めておくこと", "引っ越しの見積もりで、確認しておきたい5つのこと"], "yaku": "家庭の不用品の回収には、市区町村の許可などの決まりがあります。許可の内容を偽る表現や、「最安」など根拠のない表現は使いません。", "ph_co": "◯◯サービス", "ph_gy": "遺品整理・不用品回収", "ph_ar": "北海道札幌市"},
 {"id": "bridal", "label": "ブライダル・写真館向け", "who": "ブライダル・写真館", "gyo": "ブライダル・写真", "media": ["bridal"], "unit": "会社", "your": "御社", "ask": "何の会社", "goal": "そのまま御社の予約や問い合わせのページに来ます。", "ink": "#3A2A33", "sun": "#F5B5C8", "lemon": "#FCE3EA", "ground": "#FEF7F9", "sub": "#62555c", "line": "#eedde3", "ribbon": "見学や相談の予約が、<b>情報サイト頼み</b>なら。", "target": "結婚や記念日の準備をする人に、", "search": "結婚式や婚活、記念写真のことを調べている人が、実際に検索しているワードを、こちらで調査します。", "pains": ["情報サイトの掲載料が重い", "雰囲気や考え方が、来店の前に伝わらない"], "articles": ["結婚式の見積もりで、あとから上がりやすい項目", "七五三の写真、前撮りと当日撮影の違い", "結婚相談所の無料相談で、聞いておきたいこと"], "yaku": "「成婚率No.1」「最安」など根拠のない表現は使いません。料金は、含まれるものと条件を添えて書きます。", "ph_co": "◯◯フォトスタジオ", "ph_gy": "写真館（七五三・成人式）", "ph_ar": "長野県松本市"},
 {"id": "pet", "label": "ペット業向け", "who": "動物病院・ペットサロン", "gyo": "ペット関連", "media": ["pet"], "unit": "お店", "your": "お店", "ask": "何のお店", "goal": "そのままお店の予約や問い合わせのページに来ます。", "ink": "#3B2A1A", "sun": "#FFCB6B", "lemon": "#FFEBC4", "ground": "#FFFAEE", "sub": "#63574b", "line": "#ebe1cb", "ribbon": "新しいお客さんが、<b>広告頼み</b>なら。", "target": "ペットのことを調べている飼い主に、", "search": "ペットの体調やお手入れ、預け先のことを調べている飼い主が、実際に検索しているワードを、こちらで調査します。", "pains": ["新しい飼い主さんに、知ってもらうきっかけが少ない", "広告を出しても、近くの人に届いているか分からない"], "articles": ["子犬のトリミングは、いつから始める？", "ペットホテルに預ける前に、準備しておくこと", "猫が水を飲まないとき、家で確認したいこと"], "yaku": "動物病院の記事は、獣医療の広告の決まりに合わせて書きます。病気の診断や治療を言い切る表現は使わず、心配なときは受診をすすめる書き方にします。", "ph_co": "◯◯ペットサロン", "ph_gy": "トリミングサロン", "ph_ar": "神奈川県相模原市"},
]

CSS_ADD = """
/* 業種別の版で足したもの */
.for{display:inline-block;background:var(--ink);color:#fff;font-size:.6em;line-height:1.5;padding:2px 12px;border-radius:6px;margin:2px 0 6px}
.logo{line-height:1.25}
.logo .lf{display:block;font-size:11px;font-weight:700;color:var(--sub)}
.nayami{display:grid;gap:14px;max-width:760px;margin:0 auto}
@media(min-width:760px){.nayami{grid-template-columns:1fr 1fr}}
.nayami>div{border:3px solid var(--ink);border-radius:16px;padding:18px;background:#fff}
.nayami h3{font-family:var(--display);font-size:17px;line-height:1.5;margin:0 0 8px}
.nayami ul{margin:0;padding-left:1.2em;font-size:15px;line-height:1.8}
.yaku{max-width:760px;margin:14px auto 0;font-size:13.5px;color:var(--sub);line-height:1.75}
</style>"""

# ── 動きと手ざわり（2026-10-04 追加）────────────────────────────────
# 約束: 文言・フォーム・計測には触らない（見た目だけ）。
#   html.mo が付いたときだけ動く＝スクリプトが動かない時は今まで通り全部見える。
#   「動きを減らす」設定の人には何も動かさない。動かすのは transform と opacity が中心（重くしない）。
MOTION_CSS = """
/* 動きと手ざわり */
.kph{display:inline-block}
.what,.can p,.feat p,.case ul,.nayami ul{text-wrap:pretty}
/* 日本語を文節の切れ目で折る（対応していないブラウザでは今まで通り） */
h1,h2,h3,.what,.can p,.feat p,.fine,.pn,.yaku,li{word-break:auto-phrase;overflow-wrap:anywhere}
/* 幅320の小さい画面で「できること」が右にはみ出していた（文節で折ると最小の幅が広がるため・2026-10-04） */
.can li{grid-template-columns:84px minmax(0,1fr)}
/* 事例の数字「0回 → 82,238回」は、ひとかたまりで折る（「回」だけ次の行に落ちていた） */
.case .big b{display:inline-block;white-space:nowrap}
@media(max-width:340px){.can li{grid-template-columns:60px minmax(0,1fr);gap:12px;padding:14px 12px}.can svg{width:60px;height:60px;padding:8px}}
.can h3,.feat h3,.nayami h3{text-wrap:balance}
.pbar{position:fixed;left:0;top:0;height:4px;width:100%;background:var(--sun);border-bottom:1px solid var(--ink);transform-origin:0 50%;transform:scaleX(0);z-index:30;pointer-events:none}
header{transition:box-shadow .25s}
header.up{box-shadow:0 3px 0 var(--ink)}
header nav a{padding-bottom:2px;background:var(--sun);transition:background-size .25s}
header nav a:hover{background-size:100% 3px}
/* 最初の画面の下地：うすい点の模様と、絵のうしろの丸 */
.hero{position:relative}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;
 background-image:none;background-size:22px 22px;
 -webkit-mask-image:linear-gradient(#000,#000);mask-image:linear-gradient(#000,#000)}
@media(min-width:860px){.hero::after{content:"";position:absolute;right:-110px;top:-90px;width:520px;aspect-ratio:1;border-radius:50%;background:var(--lemon);pointer-events:none}}
.hero .in{position:relative;z-index:1}
/* 入力欄 */
input{transition:box-shadow .2s,transform .2s}
input:focus{box-shadow:0 0 0 5px var(--lemon)}
.go{transition:transform .12s,box-shadow .12s}
.box{position:relative}
#shindan{background-image:none;background-color:rgba(128,128,128,0.08)}
@media(hover:hover){
 .go:hover{transform:translateY(-2px);box-shadow:0 5px 0 var(--sun)}
 .go.y:hover{box-shadow:0 5px 0 var(--ink)}
 .feat article,.nayami>div,.case,.plan,.can li{transition:transform .18s cubic-bezier(.2,.8,.2,1),box-shadow .18s,border-color .18s}
 .feat article:hover,.nayami>div:hover,.case:hover{transform:translate(-3px,-3px);box-shadow:6px 6px 0 var(--ink)}
 .can li:hover,.plan:not(.pick):hover{transform:translate(-2px,-2px);box-shadow:5px 5px 0 var(--sun);border-color:var(--ink)}
 .plan.pick:hover{transform:translateY(-4px);box-shadow:0 10px 0 var(--sun)}
 .can svg{transition:transform .3s cubic-bezier(.3,1.6,.5,1)}
 .can li:hover svg{transform:rotate(-7deg) scale(1.06)}
 .case .see{background:var(--sun);transition:background-size .25s}
 .case .see:hover{background-size:100% 40%}
}
.go:active{transform:translateY(2px);box-shadow:none}
@media(prefers-reduced-motion:no-preference){
 @keyframes rise{from{opacity:0;transform:translateY(22px)}}
 @keyframes wipe{from{clip-path:polygon(0 0,0 0,0 100%,0 100%)}}
 @keyframes pop{0%{opacity:0;transform:scale(.55)}70%{opacity:1;transform:scale(1.07)}100%{transform:scale(1)}}
 @keyframes drop{from{opacity:0;transform:translateY(-14px) scale(.96)}}
 @keyframes floaty{50%{translate:0 -9px}}
 @keyframes ring{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--ink) 35%,transparent)}100%{box-shadow:0 0 0 9px transparent}}
 @keyframes sheen{0%,62%{transform:translateX(-130%)}100%{transform:translateX(130%)}}
 @keyframes marker{from{background-size:0 100%}}
 html.mo .hero .ribbon{animation:wipe .6s .05s cubic-bezier(.2,.8,.2,1) backwards}
 html.mo .hero h1{animation:rise .7s .15s cubic-bezier(.2,.8,.2,1) backwards}
 html.mo h1 .brand{background-repeat:no-repeat;animation:marker .7s .75s cubic-bezier(.2,.8,.2,1) backwards}
 html.mo .hero .badge{animation:pop .55s cubic-bezier(.2,.8,.2,1) backwards}
 html.mo .hero .badge:nth-child(1){animation-delay:.45s} html.mo .hero .badge:nth-child(2){animation-delay:.57s} html.mo .hero .badge:nth-child(3){animation-delay:.69s}
 html.mo .hero .cta{animation:rise .6s .85s cubic-bezier(.2,.8,.2,1) backwards}
 html.mo .hero .fine{animation:rise .6s .95s backwards}
 html.mo .phone{animation:rise .8s .3s cubic-bezier(.2,.8,.2,1) backwards,floaty 6s 1.6s ease-in-out infinite}
 html.mo .phone .sr{animation:drop .5s cubic-bezier(.2,.8,.2,1) backwards}
 html.mo .phone .sr:nth-child(5){animation-delay:.7s} html.mo .phone .sr:nth-child(4){animation-delay:.9s}
 html.mo .phone .sr:nth-child(3){animation-delay:1.1s}
 html.mo .phone .sr.new{animation:drop .5s 1.35s cubic-bezier(.2,.8,.2,1) backwards,ring 2.2s 2.1s ease-out infinite}
 /* ボタンに、ときどき光がすべる */
 .cta{position:relative;overflow:hidden;isolation:isolate}
 html.mo .cta:not(.s)::after{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;
  background:rgba(85,85,85,0.23);animation:sheen 4.2s 2.4s infinite}
 /* スクロールで出てくる（.rv はスクリプトが付ける。出たら .on。★.in は土台が中身の幅に使っている名前なので使わない★ 出おわったら外すので、マウスを乗せたときの動きと混ざらない） */
 html.mo .rv{opacity:0;transform:translateY(24px)}
 html.mo .rv.tilt{transform:translateY(30px) rotate(-1.6deg)}
 html.mo .rv.on{opacity:1;transform:none;transition:opacity .6s var(--d,0s),transform .75s var(--d,0s) cubic-bezier(.2,.8,.2,1)}
 html.mo .rule.rv{opacity:1;transform:scaleX(0)}
 html.mo .rule.rv.on{transform:none;transition:transform .6s .2s cubic-bezier(.2,.8,.2,1)}
 html.mo .case .big b{background-repeat:no-repeat}
 html.mo .case.rv .big b{background-size:0 100%}
 html.mo .case.rv.on .big b{background-size:100% 100%;transition:background-size .8s calc(var(--d,0s) + .45s) cubic-bezier(.2,.8,.2,1)}
 html.mo .feat .rv .no{transform:scale(.5);opacity:0}
 html.mo .feat .rv.on .no{transform:none;opacity:1;transition:transform .6s calc(var(--d,0s) + .15s) cubic-bezier(.3,1.6,.5,1),opacity .3s calc(var(--d,0s) + .15s)}
 .feat .no{transform-origin:0 100%}
}
"""

# 最初の描画の前に html.mo を付ける（あとから付けると、一度出たものが消えてから動いて見える）
MOTION_HEAD = ('<script>if("IntersectionObserver" in window&&!matchMedia("(prefers-reduced-motion: reduce)").matches)'
               'document.documentElement.className+=" mo"</script>')

MOTION_JS = """<script>/* 動きと手ざわり（表示だけ。フォーム・計測には触らない） */
(function(){
var d=document,mo=d.documentElement.classList.contains("mo");
/* 上の進みぐあいの線と、帯の影 */
var bar=d.createElement("div");bar.className="pbar";bar.setAttribute("aria-hidden","true");d.body.appendChild(bar);
var hd=d.querySelector("header"),tk=0;
function onS(){tk=0;var h=d.documentElement.scrollHeight-innerHeight;bar.style.transform="scaleX("+(h>0?Math.min(1,scrollY/h):0)+")";hd.classList.toggle("up",scrollY>8)}
addEventListener("scroll",function(){if(!tk)tk=requestAnimationFrame(onS)},{passive:true});onS();
/* 日本語を文節で折る：見出しが「お客さ／んが」のように単語の途中で折れるのを防ぐ（iPhoneでも効くように、言葉の切れ目ごとに包む）。
   下線つきの文字は包まない（包むと下線が消える）。数字と単位は離さない */
function phrase(sel){if(!sel||!window.Intl||!Intl.Segmenter)return;var sg=new Intl.Segmenter("ja",{granularity:"word"});
 var HEAD=/^[一-鿿々ァ-ヺー-ヿA-Za-z0-9０-９「『（(]/,KEEP=["ほったらかし集客","検索ワード","問い合わせ","無限開拓"],NOEND=/[0-9０-９,.「『（(・]$/,TAIL=/^[ぁ-ゖ、。！？!?）」』)]/;
 function sp(c){var e=d.createElement("span");e.className="kph";e.textContent=c;return e}
 d.querySelectorAll(sel).forEach(function(el){var w=d.createTreeWalker(el,NodeFilter.SHOW_TEXT),ns=[],n;while((n=w.nextNode()))ns.push(n);
  ns.forEach(function(n){var t=n.nodeValue,pa=n.parentNode;if(!t.trim()||/\\b(nb|nb2|kph)\\b/.test(pa.className||"")||getComputedStyle(pa).textDecorationLine!=="none")return;
   var ch=[],cur="",it=sg.segment(t)[Symbol.iterator](),r;
   while(!(r=it.next()).done){var x=r.value.segment;
    if(cur&&HEAD.test(x)&&!NOEND.test(cur)){
     if(/^\\s*[おご]$/.test(cur))cur+=x; /* 「お」「ご」だけなら、次の言葉の頭に付ける（お客さん・ご相談） */
     else if(/[ぁ-ゖ][おご]$/.test(cur)&&/^[一-鿿]/.test(x)){ch.push(cur.slice(0,-1));cur=cur.slice(-1)+x}
     /* 漢字どうしの続き（電話係・薬歴・記事作り）と、「探し方」「残り続ける」「飲み忘れ」のような続きは離さない */
     else if(/[一-鿿々]$/.test(cur)&&/^[一-鿿]/.test(x))cur+=x;
     else if(/[一-鿿][しりみきちいびぎけせめ]$/.test(cur)&&/^[一-鿿]/.test(x))cur+=x;
     else if(/[ァ-ヺー]$/.test(cur)&&/^[ァ-ヺー]/.test(x))cur+=x;
     else if(KEEP.some(function(k){for(var i=1;i<k.length;i++){if(cur.slice(-i)===k.slice(0,i)&&x.indexOf(k.slice(i))===0)return true}return false}))cur+=x;
     else{ch.push(cur);cur=x}}
    else if(cur&&/[」』）)]$/.test(cur)&&!/^[、。！？!?）」』)\\s]/.test(x)){ch.push(cur);cur=x} /* 「…」のあとは区切れる */
    else cur+=x}
   if(cur)ch.push(cur);
   var prev=n.previousSibling;
   /* 「探し方」＋「が、」のように、前の飾りつきの言葉に続く助詞や句読点は、前の言葉とひとまとめにする（行の頭に助詞だけが来ないように） */
   var tail=null;
   if(prev&&prev.nodeType===1&&prev.tagName!=="BR"&&TAIL.test(ch[0])&&getComputedStyle(prev).display.indexOf("inline")===0){
    var c0=ch[0],m=c0.match(/^[^、。]{0,3}[、。！？!?）」』)]+/);
    if(m){tail=m[0];if(c0.length>tail.length)ch[0]=c0.slice(tail.length);else ch.shift()}else if(c0.length<=5){tail=c0;ch.shift()}}
   var f=d.createDocumentFragment();
   if(tail){/* 短い言葉なら「前の言葉＋助詞」を折れないひとかたまりにする。長い言葉や、入りきらない時は、包まずにそのまま置く（句読点は行の頭に来ない決まりが効く） */
    if((prev.textContent||"").length+tail.length<=12){var g=d.createElement("span");g.className="kph";g.style.whiteSpace="nowrap";pa.insertBefore(g,prev);g.appendChild(prev);g.appendChild(d.createTextNode(tail));
     if(g.offsetWidth>pa.clientWidth*0.92)g.style.whiteSpace="normal"}
    else f.appendChild(d.createTextNode(tail))}
   ch.forEach(function(c){f.appendChild(sp(c))});pa.replaceChild(f,n)})})}
phrase("h1,h2,h3,.what");
if(!mo)return;
/* 数字を数え上げる。終わりは必ず元の文字に戻す（途中で止まっても数字が変わらないように） */
function count(node,delay){var t=node.nodeValue,m=t.match(/[\\d,]+(\\.\\d+)?/);if(!m)return;var to=parseFloat(m[0].replace(/,/g,""));if(!(to>0))return;
 var dec=(m[1]||"").length?m[1].length-1:0,comma=m[0].indexOf(",")>=0,pre=t.slice(0,m.index),post=t.slice(m.index+m[0].length),t0=null,dur=1100;
 function fmt(v){var s=v.toFixed(dec);return comma?Number(s).toLocaleString("en-US"):s}
 node.nodeValue=pre+fmt(0)+post;
 function step(ts){if(t0===null)t0=ts;var p=Math.min(1,(ts-t0)/dur),e=1-Math.pow(1-p,3);node.nodeValue=p<1?pre+fmt(to*e)+post:t;if(p<1)requestAnimationFrame(step)}
 setTimeout(function(){requestAnimationFrame(step)},delay);
 setTimeout(function(){node.nodeValue=t},delay+dur+400);}
d.querySelectorAll(".hero .badge b").forEach(function(b,i){var n=b.firstChild;if(n&&n.nodeType===3)count(n,500+i*120)});
/* スクロールで出てくる */
var sel="section h2,.rule,.what,.can li,.nayami>div,.yaku,.feat article,.box,.plan,.pn,.case,.last .cta,.links";
var els=[].slice.call(d.querySelectorAll(sel));
els.forEach(function(el){/* 横に並ぶ仲間は、左から順に少しずつ遅らせる */
 var sib=[].slice.call(el.parentNode.children).filter(function(x){return x.tagName===el.tagName&&els.indexOf(x)>=0});
 var i=sib.indexOf(el);if(i>0&&sib.length<7)el.style.setProperty("--d",(i*0.09)+"s");});
els.forEach(function(el){el.classList.add("rv");if(el.classList.contains("box"))el.classList.add("tilt")});
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;var el=e.target;io.unobserve(el);el.classList.add("on");
 if(el.classList.contains("case")){var b=el.querySelector(".big b"),n=b&&b.lastChild;
  if(n&&n.nodeType===3){var k=n.nodeValue.lastIndexOf("→");if(k>=0){var tail=n.splitText(k+1);count(tail,450)}}}
 setTimeout(function(){el.classList.remove("rv","on","tilt");el.style.removeProperty("--d")},2200);});},{rootMargin:"0px 0px -8% 0px",threshold:.12});
els.forEach(function(el){io.observe(el)});
/* 見えないまま残さないための保険（何かで出そびれても、4秒後には全部出す） */
setTimeout(function(){els.forEach(function(el){var r=el.getBoundingClientRect();if(r.top<innerHeight&&el.classList.contains("rv"))el.classList.add("on")})},4000);
})();</script>
"""
CSS_ADD = CSS_ADD[:-len("</style>")] + MOTION_CSS + "</style>" + MOTION_HEAD


def rep(s, old, new, n=1):
    """目印がちょうど n 回あるときだけ置き換える。違えば止まる（黙って元のまま出さない）。"""
    c = s.count(old)
    if c != n:
        sys.exit(f"目印の数が合いません（{c}回・想定{n}回）: {old[:60]}")
    return s.replace(old, new)


def li(xs):
    return "".join(f"<li>{x}</li>" for x in xs)


def build(g):
    s = BASE.read_text(encoding="utf-8")
    name = g["label"] + "ほったらかし集客"
    u = g["unit"]
    a = g["articles"]

    # 色
    s = rep(s, "--sun:#FFD23F;--lemon:#FFF3BF;--ground:#FFFBEA;--ink:#1A1A1A;--sub:#57534a;--line:#e9e2c9;",
            f"--sun:{g['sun']};--lemon:{g['lemon']};--ground:{g['ground']};--ink:{g['ink']};--sub:{g['sub']};--line:{g['line']};")
    s = s.replace('"#1A1A1A"', f'"{g["ink"]}"').replace('"#FFD23F"', f'"{g["sun"]}"')   # 絵とブラウザの帯の色
    s = rep(s, "</style>", CSS_ADD)

    # 題名・説明
    s = rep(s, "<title>あなたのお店の記事を1本無料で｜ほったらかし集客</title>",
            f"<title>{name}｜あなたの{u}の記事を1本無料で</title>")
    s = rep(s, "記事作りは、まるごとおまかせ。お店の名前・業種・メールアドレスを入れるだけで、あなたのお店のホームページに載せる記事を1本、無料でお作りします。",
            f"{g['who']}の記事作りは、まるごとおまかせ。{u}の名前・業種・メールアドレスを入れるだけで、あなたの{u}のホームページに載せる記事を1本、無料でお作りします。")

    # ★検索に載せる（2026-10-15 上野さん「検索への掲載して」）★ 土台の /ad/ は広告用なので noindex。業種のページだけ外し、
    #   自分の住所を正式な住所(canonical)にする。/ad/ そのものは触らない
    s = s.replace('<meta name="robots" content="noindex">',
                  f'<link rel="canonical" href="https://hottarakashi.mugenkaitaku.com/{g["id"]}/">')
    # LINEなどに貼ったときのカード（2026-10-15）。土台の /ad/ には無いので、業種のページにだけ足す
    s = s.replace("</head>", f'<meta property="og:title" content="{g["label"]}ほったらかし集客｜あなたの{g["unit"]}の記事を1本無料で">'
                  f'<meta property="og:url" content="https://hottarakashi.mugenkaitaku.com/{g["id"]}/"><meta property="og:type" content="website">'
                  '<meta property="og:site_name" content="ほったらかし集客"><meta property="og:image" content="https://hottarakashi.mugenkaitaku.com/icon/ogp.png">'
                  '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"></head>', 1)

    # 上の帯・最初の画面
    s = rep(s, 'data-more="logo">ほったらかし集客</a>', f'data-more="logo"><span class="lf">{g["label"]}</span>ほったらかし集客</a>')
    s = rep(s, '<div class="ribbon">書くのが<b>苦手</b>でも、時間が<b>なくても</b>。</div>', f'<div class="ribbon">{g["ribbon"]}</div>')
    s = rep(s, '<h1><small>記事作りは、まるごとおまかせ。</small><span class="brand">ほったらかし集客</span>で<br>\nお客さんに、<br>',
            f'<h1><small>記事作りは、まるごとおまかせ。</small><span class="for">{g["label"]}</span><br><span class="brand">ほったらかし集客</span>で<br>\n{g["target"]}<br>')
    s = rep(s, "<em>開始から20日</em>", "<em>菓子店・20日</em>")          # 他業種の数字だと分かるように
    s = rep(s, "<em>直近28日</em>", "<em>コンサル・28日</em>")
    s = rep(s, "お店の名前とメールを入れるだけ・約20秒・お支払いなし", f"{u}の名前とメールを入れるだけ・約20秒・お支払いなし")
    s = rep(s, '<div class="sr new"><b>調べている人への答え</b><span>あなたのホームページに公開</span></div>\n'
               '<div class="sr"><b>昨日の記事</b><span>検索とAIが読みに来ています</span></div>\n'
               '<div class="sr"><b>一昨日の記事</b><span>検索から人が来はじめました</span></div>',
            f'<div class="sr new"><b>{a[0]}</b><span>記事の例・{g["your"]}のホームページに公開</span></div>\n'
            f'<div class="sr"><b>{a[1]}</b><span>記事の例</span></div>\n'
            f'<div class="sr"><b>{a[2]}</b><span>記事の例</span></div>')

    # とは・できること
    s = rep(s, "<h2>ほったらかし集客とは？</h2>", f'<h2><span class="nb">{g["label"]}</span><wbr><span class="nb">ほったらかし集客とは？</span></h2>')
    s = rep(s, '<p class="what">検索ワードの調査から記事の公開までを代行する、', f'<p class="what">{g["who"]}のために、検索ワードの調査から記事の公開までを代行する、')
    s = rep(s, "<p>思いつきではなく、実際に検索されているワードを、こちらで調査します。</p>", f"<p>{g['search']}</p>")
    s = rep(s, "そのままお店や問い合わせページに来ます。", g["goal"])

    # 業種のお悩みと記事の例（できること と 3つの特徴 のあいだ）
    block = (f'<section><div class="in">\n<h2><span class="nb">{g["who"]}の、</span><wbr><span class="nb">こんなお悩みに</span></h2><div class="rule"></div>\n<div class="nayami">\n'
             f'<div><h3>よくあるお悩み</h3><ul>{li(g["pains"])}</ul></div>\n'
             f'<div><h3>たとえば、こんな記事を作ります</h3><ul>{li(a)}</ul></div>\n</div>\n'
             f'<p class="yaku">書き方の約束：{g["yaku"]}検索の順位や売上をお約束するものではありません。</p>\n</div></section>\n\n')
    s = rep(s, '<section><div class="in">\n<h2>3つの特徴</h2>', block + '<section class="tint"><div class="in">\n<h2>3つの特徴</h2>')

    # 記事を作る箱
    s = rep(s, '<span class="nb">あなたのお店の記事を、</span>', f'<span class="nb">あなたの{u}の記事を、</span>')
    s = rep(s, "お店の名前・何のお店か・メールアドレスを入れるだけ。", f"{u}の名前・{g['ask']}か・メールアドレスを入れるだけ。")
    s = rep(s, 'placeholder="例：CAKE LAB"', f'placeholder="例：{g["ph_co"]}"')
    if u not in ("会社", "お店"):
        s = rep(s, '<label for="co">お店・会社の名前</label>', f'<label for="co">{u}の名前</label>')
    s = rep(s, '<label for="gy">何のお店ですか</label>', f'<label for="gy">{g["ask"]}ですか</label>')
    s = rep(s, 'placeholder="例：チーズケーキ専門店"', f'placeholder="例：{g["ph_gy"]}"')
    s = rep(s, 'placeholder="例：東京都練馬区"', f'placeholder="例：{g["ph_ar"]}"')
    s = rep(s, "お店の名前と、何のお店かを入れてください", f"{u}の名前と、{g['ask']}かを入れてください")

    # 事例（この業種の事例が無いうちは、無いと書く）
    if not g.get("case_same"):
        s = rep(s, "<h2>実際のお客さまの数字と、公開している記事です</h2>", "<h2>ほかの業種のお客さまの数字と、公開している記事です</h2>")
        s = rep(s, '<p class="pn">数字は2026年9月30日時点の実測です',
                f'<p class="pn">{g["gyo"]}のお客さまの掲載事例は、まだありません。上は、ほかの業種のお客さまの数字です。数字は2026年9月30日時点の実測です')

    # 最後・フッター・計測の目印
    s = rep(s, "<h2>まずは、あなたのお店の記事を1本。</h2>", f"<h2>まずは、あなたの{u}の記事を1本。</h2>")
    s = rep(s, "ほったらかし集客 ／ 運営：無限開拓株式会社", f"{name} ／ 運営：無限開拓株式会社")
    s = rep(s, ' variant=/imageG/i.test(q.get("utm_content")||"")?"G":"H",', f' variant="{g["id"]}",')   # どの業種のページかを記録に残す

    s = rep(s, "</body></html>", MOTION_JS + "</body></html>")   # 動きと手ざわり

    if u != "お店" and "お店" in s.split("<script>(function")[0].split("</style>")[1].replace("お店・会社の名前", ""):
        sys.exit("「お店」が残っています")
    out = HERE / g["id"] / "index.html"
    out.parent.mkdir(exist_ok=True)
    sys.path.insert(0, str(HERE.parent)); import price_2026_10   # 2026-10-17 値上げ。書き出す直前に新料金へそろえる
    s = price_2026_10.apply(s)
    # ★検索される言葉に合わせる（2026-11-22 上野さん「全部チェックお願い」）★ 題名・説明・見出しの小さい字・よくある質問3問。
    #   中身は ../lp_kensaku_kyouka.py の SEO 表（本番に直接当てる物と同じ）。作り直しても元の題名に戻らないように
    import lp_kensaku_kyouka as KK
    if g["id"] in KK.SEO:
        s, _t, _d, errs = KK.patch(s, g["id"])
        if errs:
            sys.exit(f"検索の言葉の目印が合いません {g['id']}: {errs}")
    out.write_text(s, encoding="utf-8")
    print(f"{g['id']}: {name} → {out.relative_to(HERE.parent)}（{len(s):,}字）")


if __name__ == "__main__":
    want = sys.argv[1:]   # 業種idを並べると、その業種だけ作る（無ければ全部）
    for g in GYOSHU:
        if not want or g["id"] in want:
            build(g)
