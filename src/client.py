import os

import httpx

API_BASE = "https://api-prod.codetree.ai"
SIGNIN_PATH = "/api/v2/api-token-auth/"

# X-Device-Info 가 없거나 JSON 이 아니면 api-token-auth 가 403 을 준다.
# 값 자체는 검증하지 않아서 형식만 맞으면 되므로 기본값을 내장한다.
DEFAULT_DEVICE_INFO = '{"os":"linux","browser":"chrome"}'


def _headers(jwt=None):
    h = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.codetree.ai",
        "Referer": "https://www.codetree.ai/",
        "X-Device-Info": os.environ.get("CODETREE_DEVICE_INFO") or DEFAULT_DEVICE_INFO,
        "X-TZ-Offset": "9",
    }
    if jwt:
        h["Authorization"] = f"JWT {jwt}"
    return h


def login() -> str:
    user = os.environ.get("CODETREE_ID", "")
    pw = os.environ.get("CODETREE_PW", "")
    if not user or not pw:
        raise RuntimeError("CODETREE_ID / CODETREE_PW 시크릿이 비어있음")
    r = httpx.post(
        f"{API_BASE}{SIGNIN_PATH}",
        json={"username": user, "password": pw},
        headers=_headers(),
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access"]


def _get(path: str, jwt: str):
    r = httpx.get(f"{API_BASE}{path}", headers=_headers(jwt), timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_progress(jwt: str) -> list:
    return _get("/api/v2/trails/progress/", jwt)


def fetch_streak(jwt: str) -> dict:
    return _get("/api/v2/streak/", jwt)


def fetch_me(jwt: str) -> dict:
    return _get("/api/v2/users/me/", jwt)
