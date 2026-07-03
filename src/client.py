import os

import httpx

API_BASE = "https://api-prod.codetree.ai"
SIGNIN_PATH = "/api/v2/api-token-auth/"


def _headers(jwt=None):
    # X-Device-Info 가 없으면 api-token-auth 가 403("자격증명 미제공") 을 준다.
    # 로그인된 브라우저의 요청 헤더에서 복사한 값을 그대로 쓰면 된다.
    h = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.codetree.ai",
        "Referer": "https://www.codetree.ai/",
        "X-Device-Info": os.environ.get("CODETREE_DEVICE_INFO", ""),
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
