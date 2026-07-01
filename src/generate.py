"""코드트리 뱃지 생성기.

코드트리에 로그인해 학습 진도를 가져오고, result/ 아래에 SVG 뱃지들을 쓴다.
GitHub Actions 가 주기적으로 실행해 커밋하면, README 에서는
raw.githubusercontent.com 경로로 이 SVG 를 바로 참조할 수 있다.

로컬 미리보기(자격증명 없이):  python src/generate.py --sample
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cards
import client
import normalize as norm

RESULT = Path(__file__).resolve().parent.parent / "result"
SAMPLE = Path(__file__).resolve().parent / "sample_meta.json"


def fetch_meta() -> dict:
    jwt = client.login()
    return norm.normalize(
        client.fetch_progress(jwt),
        client.fetch_streak(jwt),
        client.fetch_me(jwt),
    )


def render_all(meta: dict) -> list[str]:
    RESULT.mkdir(parents=True, exist_ok=True)
    written = []
    for name in ("summary", "streak", "xp", "types", "ladder"):
        (RESULT / f"{name}.svg").write_text(cards.render(meta, name), encoding="utf-8")
        written.append(f"{name}.svg")
    for i in range(len(meta.get("courses", []))):
        (RESULT / f"course_{i}.svg").write_text(cards.course_card(meta, i), encoding="utf-8")
        written.append(f"course_{i}.svg")
    return written


def main() -> int:
    if "--sample" in sys.argv:
        meta = json.loads(SAMPLE.read_text(encoding="utf-8"))
        print("샘플 메타로 렌더링 (자격증명 미사용)")
    else:
        meta = fetch_meta()
        s = meta["summary"]
        print(f"메타 수신: {s['solved']}/{s['total']} solved, streak {meta['streak']['current']}")

    written = render_all(meta)
    print(f"result/ 에 {len(written)}개 SVG 생성: {', '.join(written)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
