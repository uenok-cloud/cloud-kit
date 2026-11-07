# CloseOps 画像プロンプト（Codex / 画像生成AI用）

LPは画像なしで完成しています（実績セクションの「1000本の光が一点に集まる」演出はページ内で描画）。
Codex などで画像を作る場合は、以下をそのまま貼ってください。色は LP に合わせています。

## 1. OGP画像（SNSシェア用 1200×630）
Dark navy background (#0F1B2D). Thousands of tiny white light particles streaming from the left
and converging into a single vermilion (#D8402B) point on the right, like a circular Japanese hanko
seal stamped on paper. Large bold Japanese text on the left: "一騎当千のクロージング".
Small text below: "AI・IT企業専用 営業チーム CloseOps". Minimal, sharp, no people, no stock-photo look.

## 2. ヒーロー横のビジュアル（正方形 1200×1200）
Top-down view of a dark desk at night. A signed contract with a bright vermilion circular seal
reading "成約". Around it, faint holographic UI cards showing a sales pipeline (リード → 商談 → 成約).
Cinematic lighting, navy and vermilion only, high contrast, photorealistic.

## 差し替え方法
画像を `lp/` に置いて、`closeops.html` の `.pipe`（ヒーロー右側）を `<img src="hero.png" alt="">` に置き換えてください。
