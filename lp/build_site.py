# 成約職人LPを、どのホスティングでも動く単体のHTML（site/index.html）に書き出す
import re, pathlib
here = pathlib.Path(__file__).parent
src = (here / "closeops.html").read_text()
title = re.search(r"<title>(.*?)</title>", src).group(1)
desc = re.search(r'<meta name="description" content="(.*?)">', src).group(1)
body = re.sub(r'<title>.*?</title>\n|<meta name="(description|claude:viewport-fit-sides)"[^>]*>\n', "", src)
head = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}｜AI・IT企業専用 クロージングチーム</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://seiyaku.mugenkaitaku.com/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://seiyaku.mugenkaitaku.com/">
<meta property="og:title" content="{title}｜AI・IT企業専用 クロージングチーム">
<meta property="og:description" content="{desc}">
<meta name="twitter:card" content="summary_large_image">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0;font:14px/1.5 system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
'''
out = head + body.replace("<style>", "<style>", 1)
# 最初の <style> の前で head を閉じ、残りを body に入れる
first_header = out.index('<header class="hdr">')
out = out[:first_header] + "</head>\n<body>\n" + out[first_header:] + "</body>\n</html>\n"
(here / "site" / "index.html").write_text(out)
# GitHub Pages 用（リポジトリ直下の docs/ を公開。独自ドメインは CNAME で指定）
docs = here.parent / "docs"
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(out)
(docs / "CNAME").write_text("seiyaku.mugenkaitaku.com\n")
(docs / ".nojekyll").write_text("")
print("wrote site/index.html and docs/index.html", len(out), "bytes")
