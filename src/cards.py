import datetime
import html
import math

# 코드트리 메타 → SVG 카드. GitHub README 에 <img> 로 박는 용도라
# 폰트는 뷰어 시스템 폰트에 맡기고(한글 포함), 색/도형만 우리가 그린다.

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Apple SD Gothic Neo','Malgun Gothic',sans-serif"

BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
TRACK = "#21262d"
TEXT = "#e6edf3"
MUTED = "#7d8590"
CYAN = "#2ee6d6"
GREEN = "#3fb950"
AMBER = "#d29922"
FLAME1 = "#ffb84d"
FLAME2 = "#ff6b35"

# 코스 7단계: 쉬움(시안)→어려움(핑크) 으로 자연스럽게 흐르는 램프
COURSE_RAMP = ["#2ee6d6", "#39d98a", "#58a6ff", "#6e7bff", "#a371f7", "#cc6bf0", "#f778ba"]


def _esc(s):
    return html.escape(str(s), quote=True)


def _pct(a, b):
    return (a / b) if b else 0.0


def _frame(w, h, body, title=None, extra_defs=""):
    head = ""
    if title:
        head = (
            f'<text x="20" y="30" font-family="{FONT}" font-size="13" font-weight="700" '
            f'fill="{MUTED}" letter-spacing="0.5">{_esc(title)}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" font-family="{FONT}">'
        f"<defs>"
        f'<linearGradient id="bgg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#161b22"/><stop offset="1" stop-color="#0d1117"/>'
        f"</linearGradient>{extra_defs}</defs>"
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="url(#bgg)" stroke="{BORDER}"/>'
        f"{head}{body}</svg>"
    )


def _bar(x, y, w, h, pct, fill, track=TRACK):
    pct = max(0.0, min(1.0, pct))
    fw = max(0.0, w * pct)
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{track}"/>'
    if fw > 0:
        out += f'<rect x="{x}" y="{y}" width="{fw:.1f}" height="{h}" rx="{h/2}" fill="{fill}"/>'
    return out


def _ring(cx, cy, r, sw, pct, grad):
    pct = max(0.0, min(1.0, pct))
    c = 2 * math.pi * r
    track = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TRACK}" stroke-width="{sw}"/>'
    if pct <= 0:
        return track  # 0% 면 진행 아크를 안 그린다(라운드캡 점 방지)
    dash = c * pct
    return (
        track
        + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{grad}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-dasharray="{dash:.1f} {c:.1f}" '
        f'transform="rotate(-90 {cx} {cy})"/>'
    )


# ── 카드들 ──────────────────────────────────────────────

def summary_card(m):
    s = m["summary"]
    solved, total = s["solved"], s["total"]
    pct = _pct(solved, total)
    sbt = s.get("solved_by_type", {})
    user = m.get("profile", {}).get("username", "")
    defs = (
        '<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="#58a6ff"/>'
        "</linearGradient>"
    )
    cx, cy, r = 78, 80, 46
    body = (
        _ring(cx, cy, r, 11, pct, "url(#ring)")
        + f'<text x="{cx}" y="{cy+2}" text-anchor="middle" font-size="26" font-weight="800" fill="{TEXT}">{pct*100:.1f}%</text>'
        + f'<text x="{cx}" y="{cy+18}" text-anchor="middle" font-size="10" fill="{MUTED}">complete</text>'
        # 우측 텍스트 + 전체 진척 바
        + f'<text x="150" y="30" font-size="13" font-weight="700" fill="{CYAN}" letter-spacing="0.5">CODETREE</text>'
        + f'<text x="150" y="54" font-size="17" font-weight="700" fill="{TEXT}">@{_esc(user)}</text>'
        + f'<text x="150" y="86" font-size="30" font-weight="800" fill="{TEXT}">{solved}'
        + f'<tspan font-size="15" font-weight="600" fill="{MUTED}"> / {total} solved</tspan></text>'
        + _bar(150, 98, 290, 8, pct, CYAN)
        + f'<text x="150" y="132" font-size="12" fill="{MUTED}">'
        + f'<tspan fill="{CYAN}">●</tspan> Problem {sbt.get("Problem",0)}   '
        + f'<tspan fill="{AMBER}">●</tspan> Test {sbt.get("Test",0)}   '
        + f'<tspan fill="#a371f7">●</tspan> Intro {sbt.get("Introduction",0)}</text>'
    )
    return _frame(460, 150, body, extra_defs=defs)


def streak_card(m):
    # 대칭 스탯 카드: 현재 연속 · 최고 연속 · 총 학습일. 하단 점은 최근 14일 학습 여부.
    # 최고/총은 누적 학습일(streak.days)로 계산한다. 누적이 없으면 history 로 대체.
    st = m.get("streak", {})
    cur = st.get("current", 0)
    day_strs = st.get("days") or [
        d.get("gained_at") for d in st.get("history", []) if d.get("exp", 0) > 0
    ]
    days = set()
    for s in day_strs:
        try:
            days.add(datetime.date.fromisoformat(s))
        except (TypeError, ValueError):
            pass
    best = run = 0
    for d in sorted(days):
        run = run + 1 if (d - datetime.timedelta(days=1)) in days else 1
        best = max(best, run)
    best = max(best, cur)
    total = max(len(days), cur)

    defs = (
        '<linearGradient id="flame" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{FLAME1}"/><stop offset="1" stop-color="{FLAME2}"/>'
        "</linearGradient>"
    )
    flame = (
        '<path transform="translate(86 19) scale(0.95)" fill="url(#flame)" '
        'd="M12 0c2 4 6 5 6 10a6 6 0 1 1-12 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-2-4 0-9z"/>'
    )

    cols = [(cur, "현재 연속", CYAN), (best, "최고 연속", TEXT), (total, "총 학습일", TEXT)]
    body = flame
    for (val, label, color), x in zip(cols, (105, 230, 355)):  # 460 폭 대칭 3분할
        body += (
            f'<text x="{x}" y="88" text-anchor="middle" font-size="44" font-weight="800" fill="{color}">{val}</text>'
            f'<text x="{x}" y="109" text-anchor="middle" font-size="11.5" font-weight="600" fill="{MUTED}">{label}</text>'
        )

    # 최근 14일 학습 여부 점
    n, dot, gap = 14, 11, 5
    sx = (460 - (n * dot + (n - 1) * gap)) / 2
    dy = 128
    today = datetime.date.today()
    recent = 0
    for i in range(n):
        day = today - datetime.timedelta(days=n - 1 - i)
        on = day in days
        if on:
            recent += 1
        body += f'<rect x="{sx + i*(dot+gap):.1f}" y="{dy}" width="{dot}" height="{dot}" rx="3" fill="{CYAN if on else TRACK}"/>'
    body += f'<text x="230" y="{dy+27}" text-anchor="middle" font-size="9.5" fill="{MUTED}">최근 {n}일 · {recent}일 학습</text>'
    return _frame(460, 168, body, title="STREAK", extra_defs=defs)


def ladder_card(m):
    courses = sorted(m.get("courses", []), key=lambda c: c.get("order", 0))
    # 현재 코스 = solved>0 중 가장 윗단계
    cur_alias = None
    for c in courses:
        if c.get("solved", 0) > 0:
            cur_alias = c["alias"]
    rows = ""
    y = 48
    for i, c in enumerate(courses):
        pct = _pct(c["solved"], c["total"])
        color = COURSE_RAMP[i % len(COURSE_RAMP)]
        is_cur = c["alias"] == cur_alias
        label = c["name"]
        if len(label) > 24:
            label = label[:23] + "…"
        mark = f'<tspan fill="{CYAN}" font-weight="700"> ◀</tspan>' if is_cur else ""
        rows += (
            f'<text x="20" y="{y-4}" font-size="11.5" font-weight="{700 if is_cur else 500}" '
            f'fill="{TEXT if is_cur else MUTED}">{_esc(label)}{mark}</text>'
            f'<text x="440" y="{y-4}" text-anchor="end" font-size="11" fill="{MUTED}">'
            f'{c["solved"]}/{c["total"]} · {pct*100:.0f}%</text>'
            + _bar(20, y, 420, 7, pct, color)
        )
        y += 28
    return _frame(460, 252, rows, title="COURSE LADDER")


def xp_card(m):
    hist = list(reversed(m.get("streak", {}).get("history", [])))  # 오래된→최신
    goal = hist[0].get("goal", 140) if hist else 140
    exps = [d.get("exp", 0) for d in hist]
    mx = max(exps + [goal]) * 1.15 or 1
    x0, y0, plotw, ploth = 20, 50, 420, 78
    n = len(hist) or 1
    bw = min(26, plotw / n * 0.6)
    gap = plotw / n
    gy = y0 + ploth - ploth * (goal / mx)
    goal_y = gy
    bars = ""
    for i, d in enumerate(hist):
        ex = d.get("exp", 0)
        bh = ploth * (ex / mx)
        bx = x0 + i * gap + (gap - bw) / 2
        by = y0 + ploth - bh
        met = ex >= goal
        is_today = i == len(hist) - 1
        col = GREEN if met else "#373e47"
        bars += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{max(2,bh):.1f}" rx="3" fill="{col}"/>'
        if is_today:
            bars += f'<rect x="{bx-1.5:.1f}" y="{by-1.5:.1f}" width="{bw+3:.1f}" height="{max(2,bh)+3:.1f}" rx="4" fill="none" stroke="{CYAN}" stroke-width="1.5"/>'
    goal_line = (
        f'<line x1="{x0}" y1="{goal_y:.1f}" x2="{x0+plotw}" y2="{goal_y:.1f}" stroke="{AMBER}" '
        f'stroke-width="1" stroke-dasharray="4 3" opacity="0.75"/>'
    )
    body = (
        f'<text x="440" y="30" text-anchor="end" font-size="11" fill="{MUTED}">최근 {n}일 '
        f'· <tspan fill="{AMBER}">goal {goal}</tspan></text>'
        + goal_line + bars
    )
    return _frame(460, 160, body, title="DAILY XP")


def types_card(m):
    s = m["summary"]
    sbt, tbt = s.get("solved_by_type", {}), s.get("total_by_type", {})
    rows = [("Problem", CYAN), ("Test", AMBER), ("Introduction", "#a371f7")]
    y = 58
    body = ""
    for name, col in rows:
        sv, tt = sbt.get(name, 0), tbt.get(name, 0)
        pct = _pct(sv, tt)
        body += (
            f'<text x="20" y="{y-7}" font-size="13" font-weight="600" fill="{TEXT}">{name}</text>'
            f'<text x="440" y="{y-7}" text-anchor="end" font-size="11.5" fill="{MUTED}">'
            f'{sv} / {tt} · {pct*100:.0f}%</text>'
            + _bar(20, y, 420, 10, pct, col)
        )
        y += 42
    return _frame(460, y - 2, body, title="BY TYPE")


# 코스 alias → (트레일 한글명, 트레일 번호). 코드트리 UI 의 실제 명칭을 따른다.
COURSE_LABEL = {
    "codetree-101": ("프로그래밍 시작", "TRAIL 0"),
    "novice-low": ("프로그래밍 기초", "TRAIL 1"),
    "novice-mid": ("프로그래밍 연습", "TRAIL 2"),
    "novice-high": ("자료구조 알고리즘", "TRAIL 3"),
    "intermediate-low": ("알고리즘 입문", "TRAIL 4"),
    "intermediate-mid": ("알고리즘 기본", "TRAIL 5"),
    "intermediate-high": ("알고리즘 실전", "TRAIL 6"),
}


def course_card(m, idx):
    courses = sorted(m.get("courses", []), key=lambda c: c.get("order", 0))
    if idx < 0 or idx >= len(courses):
        raise KeyError(idx)
    c = courses[idx]
    pct = _pct(c["solved"], c["total"])
    color = COURSE_RAMP[idx % len(COURSE_RAMP)]
    label, lv = COURSE_LABEL.get(c["alias"], (c["name"][:10], f"LV {idx}"))
    done = pct >= 1.0
    W, H = 118, 150
    cx, cy, r = 59, 62, 30
    gid = f"cr{idx}"
    defs = (
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{color}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0.5"/></linearGradient>'
    )
    body = (
        f'<rect x="14" y="0" width="{W-28}" height="3" rx="1.5" fill="{color}"/>'  # 상단 액센트
        + f'<text x="{cx}" y="26" text-anchor="middle" font-size="9" font-weight="700" '
          f'fill="{color}" letter-spacing="1">{lv}</text>'
        + _ring(cx, cy, r, 7, pct if not done else 1.0, "url(#%s)" % gid)
        + f'<text x="{cx}" y="{cy+7}" text-anchor="middle" font-size="19" font-weight="800" fill="{TEXT}">'
          f'{pct*100:.0f}<tspan font-size="10" fill="{MUTED}">%</tspan></text>'
        + f'<text x="{cx}" y="117" text-anchor="middle" font-size="11" font-weight="700" fill="{TEXT}">{_esc(label)}</text>'
        + f'<text x="{cx}" y="135" text-anchor="middle" font-size="10" fill="{MUTED}">{c["solved"]} / {c["total"]}</text>'
    )
    return _frame(W, H, body, extra_defs=defs)


CARDS = {
    "summary": summary_card,
    "streak": streak_card,
    "ladder": ladder_card,
    "xp": xp_card,
    "types": types_card,
}


def render(meta, name):
    fn = CARDS.get(name)
    if not fn:
        raise KeyError(name)
    return fn(meta)
