from datetime import datetime, timezone

PASSED = "Passed"


def _cards(course):
    # 코스 > 챕터 > 레슨 > 카드. 가끔 레슨 없이 챕터에 카드가 바로 붙는다.
    for ch in course.get("chapters", []):
        lessons = ch.get("lessons")
        for grp in (lessons if lessons is not None else [ch]):
            for card in grp.get("curated_cards", []):
                yield card


def normalize(progress: list, streak: dict, me: dict) -> dict:
    total = solved = 0
    sbt, tbt = {}, {}
    courses = []
    for c in progress:
        ct = cs = 0
        for card in _cards(c):
            typ = card.get("type", "?")
            total += 1
            ct += 1
            tbt[typ] = tbt.get(typ, 0) + 1
            if card.get("progress_status") == PASSED:
                solved += 1
                cs += 1
                sbt[typ] = sbt.get(typ, 0) + 1
        courses.append({"name": c.get("name"), "alias": c.get("alias"), "order": c.get("order", 0), "solved": cs, "total": ct})

    courses.sort(key=lambda x: x.get("order", 0))
    return {
        "schema": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "profile": {"username": (me or {}).get("username", "")},
        "summary": {"solved": solved, "total": total, "solved_by_type": sbt, "total_by_type": tbt},
        "courses": courses,
        "streak": {"current": (streak or {}).get("current_streak", 0), "history": (streak or {}).get("history", [])},
    }
