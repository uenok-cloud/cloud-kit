"""商談用の検索数表示ツール。

    uvicorn app:app --host 0.0.0.0 --port 8010

地域とサービス名を入れると、「○○市で○○を検索している人は月にこれくらい」を数秒で出す。
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

import keywords

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="検索数チェック（商談用）", docs_url=None, redoc_url=None, openapi_url=None)


class BasicAuth(BaseHTTPMiddleware):
    """既存の商談サンプルと同じく、合言葉（APP_USER / APP_PASSWORD）で全体を守る。未設定なら素通し。"""

    async def dispatch(self, request: Request, call_next):
        user, pw = os.environ.get("APP_USER"), os.environ.get("APP_PASSWORD")
        if user and pw and request.url.path != "/healthz":
            ok = False
            auth = request.headers.get("authorization", "")
            if auth.startswith("Basic "):
                import base64
                try:
                    u, _, p = base64.b64decode(auth[6:]).decode("utf-8").partition(":")
                    ok = secrets.compare_digest(u, user) and secrets.compare_digest(p, pw)
                except Exception:
                    ok = False
            if not ok:
                return Response("合言葉が必要です", status_code=401, headers={"WWW-Authenticate": 'Basic realm="search-demand"'})
        resp = await call_next(request)
        resp.headers["X-Robots-Tag"] = "noindex, nofollow"
        return resp


app.add_middleware(BasicAuth)


@app.get("/healthz")
def healthz():
    return {"ok": True, "ads_connected": keywords.dfs_auth() is not None}


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/api/lookup")
async def api_lookup(
    area: str = Query("", max_length=40, description="地域（例：千葉市）"),
    service: str = Query(..., min_length=1, max_length=40, description="サービス名（例：外壁塗装）"),
    extra: str = Query("", max_length=300, description="追加で調べたい語（カンマ区切り）"),
    pref: str = Query("", max_length=10, description="都道府県（任意。市名から推定できない時）"),
):
    extras = [x.strip() for x in extra.replace("、", ",").split(",") if x.strip()]
    if len(extras) > 20:
        raise HTTPException(400, "追加の語は 20 個までです")
    data = await keywords.lookup(area, service, extras, pref or None)
    return JSONResponse(data)
