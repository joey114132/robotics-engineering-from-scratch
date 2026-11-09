# 화면들: home, map, stats, mission 카드, 공통 HUD 줄
import datetime as dt
import re

from rich import box
from rich.cells import cell_len
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from . import motion
from . import progress as P
from . import ui as U

_INLINE = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*)")


def inline_md(s, plain=False):
    """`code` 와 **bold** 만 처리하는 작은 인라인 마크다운. plain 에서는 백틱을 그대로 둔다."""
    t = Text()
    for part in _INLINE.split(s):
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            t.append(part if plain else part[1:-1], style="" if plain else "bold accent")
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            t.append(part[2:-2], style="bold")
        else:
            t.append(part)
    return t


def lesson_frac(state, lid):
    return min(len(state["q"].get(lid, {})), P.QUESTIONS_PER_LESSON) / P.QUESTIONS_PER_LESSON * 0.8 + 0.2 * bool(state["m"].get(lid))


def hud(u, state, today):
    xp = state["xp"]
    i, into, span = P.level_progress(xp)
    sep = Text("   ", style="muted")
    t = Text()
    t.append("XP ", style="muted"), t.append(str(xp), style="bold")
    t.append_text(sep)
    t.append(u.t("Level ", "레벨 ") + f"{i + 1} ", style="muted"), t.append(P.level_name(xp, u.lang), style="bold accent")
    t.append(" "), t.append_text(U.bar_text(into / span, 10, u.plain)), t.append(f" {into}/{span}" if i < len(P.LEVELS) - 1 else " max", style="muted")
    t.append_text(sep)
    st = P.streak(state, today)
    t.append(u.t("streak ", "연속 ") + (f"{st} " + u.t("day" if st == 1 else "days", "일")), style="muted" if st == 0 else "warn")
    t.append_text(sep)
    t.append(u.t("badges ", "배지 ") + str(len(state["badges"])), style="muted")
    return t


def next_hint(u, course, state):
    nxt = course.next_lesson(state, P.lesson_done)
    if not nxt:
        return Text(u.t("Every lesson is done. Run robo daily to review.", "모든 레슨을 마쳤습니다. robo daily 로 복습을 이어 가세요."), style="ok")
    t = Text()
    t.append(u.t("Next  ", "다음  "), style="muted"), t.append(u.g["arrow"] + " ", style="accent")
    t.append(f"{nxt.short}  ", style="bold accent"), t.append(nxt.title(u.lang), style="bold")
    return t, nxt


def phase_progress(course, state, phase):
    done = sum(P.lesson_done(state, l.id) for l in phase.lessons)
    frac = sum(lesson_frac(state, l.id) for l in phase.lessons) / len(phase.lessons)
    return done, frac


def home_tagline(u, course):
    return u.t(f"{len(course.lessons)} lessons in {len(course.phases)} phases", f"{len(course.phases)}개 단계 · 레슨 {len(course.lessons)}개")


def phase_lines(u, course, state, scale=1.0):
    """단계별 진행 막대 줄들. scale(0~1)로 막대가 차오르는 정도를 정한다(숫자 표시는 그대로)."""
    w = u.read_width
    bar_w = 14 if w < 80 else 22
    title_w = min(34, w - (2 + 3 + 2 + bar_w + 2 + 6))
    out = []
    for idx, ph in enumerate(course.phases):
        done, frac = phase_progress(course, state, ph)
        t = Text("  ")
        t.append(ph.no + " ", style=U.phase_color(idx, u.dark) if not u.plain else "")
        t.append(" " + U.pad(U.trunc(ph.title(u.lang), title_w - 1), title_w), style="bold" if done == len(ph.lessons) else "")
        t.append_text(U.bar_text(frac * scale, bar_w, u.plain, style=U.phase_color(idx, u.dark)))
        t.append(f"  {done}/{len(ph.lessons)}".rjust(7), style="muted" if done < len(ph.lessons) else "ok")
        out.append(t)
    return out


def home(u, course, state, today, head=True):
    """head=False 면 배너와 HUD 는 이미 인트로가 그렸다."""
    if head:
        U.print_banner(u, tagline=home_tagline(u, course))
        u.para(Text("  ") + hud(u, state, today))
    u.print()
    u.rule(u.t("Phases", "단계"), u.read_width)

    def build(scale):
        t = Text("\n").join(phase_lines(u, course, state, scale))
        t.no_wrap, t.overflow = True, "crop"
        return t
    motion.animate(u, build)
    u.print()
    hint = next_hint(u, course, state)
    if isinstance(hint, tuple):
        u.print(Text("  ") + hint[0])
        n = hint[1].short
        u.para(Text(f"        robo read {n}   robo quiz {n}   robo mission {n}", style="muted"), indent=8)
    else:
        u.print(Text("  ") + hint)
    u.print(Text("  " + u.t("robo --help lists every command", "robo --help 로 모든 명령을 봅니다"), style="muted"))


def lesson_map(u, course, state):
    w = u.read_width
    nxt = course.next_lesson(state, P.lesson_done)
    u.print()
    for idx, ph in enumerate(course.phases):
        done, _ = phase_progress(course, state, ph)
        col = U.phase_color(idx, u.dark)
        head = Text()
        head.append(f"{ph.no} ", style=col if not u.plain else "bold")
        head.append(ph.title(u.lang), style="bold")
        count = f"{done}/{len(ph.lessons)}"
        gap = max(1, w - 2 - cell_len(head.plain) - cell_len(count))
        head.append(" " * gap), head.append(count, style="ok" if done == len(ph.lessons) else "muted")
        u.print(Text("  ") + head, overflow="crop", no_wrap=True)
        last = len(ph.lessons) - 1
        for i, les in enumerate(ph.lessons):
            stt = P.lesson_state(state, les.id)
            is_next = nxt is not None and les.id == nxt.id
            glyph, style = (u.g["done"], "ok") if stt == "done" else (u.g["cur"], "bold accent") if is_next else (u.g["part"], "warn") if stt == "partial" else (u.g["todo"], "muted")
            branch = ("└─" if i == last else "├─") if not u.plain else ("`-" if i == last else "|-")
            t = Text("  ")
            t.append(branch + " ", style=col if not u.plain else "")
            t.append(U.pad(glyph, 3 if u.plain else 1) + " ", style=style)
            t.append(les.short + "  ", style="muted" if stt != "done" else "ok")
            room = w - cell_len(t.plain) - 1
            t.append(U.trunc(les.title(u.lang), room), style="bold" if is_next else "" if stt == "done" else "muted" if stt == "new" else "")
            u.print(t, no_wrap=True, overflow="crop")
        u.print()
    legend = Text("  ")
    for key, label, style in (("done", u.t("done", "완료"), "ok"), ("cur", u.t("next", "다음"), "bold accent"), ("part", u.t("started", "진행 중"), "warn"), ("todo", u.t("not started", "시작 전"), "muted")):
        legend.append(u.g[key] + " ", style=style), legend.append(label + "   ", style="muted")
    u.print(legend)


def mission_card(u, lesson, state):
    body = lesson.fun(u.lang).get("mission") or u.t("This lesson has no mission.", "이 레슨에는 미션이 없습니다.")
    done = bool(state["m"].get(lesson.id))
    inner = Text()
    inner.append_text(inline_md(body, u.plain))
    inner.append("\n\n")
    if done:
        inner.append(u.g["good"] + " " + u.t("Mission done.", "미션 완료."), style="ok")
    else:
        inner.append(u.t(f"When you have run it: robo mission {lesson.short} --done   (+{P.XP_PER_MISSION} XP once)",
                         f"해 봤다면 robo mission {lesson.short} --done   (한 번만 +{P.XP_PER_MISSION} XP)"), style="muted")
    title = Text(u.t(" Mission ", " 미션 ") + lesson.short + " ", style="bold accent")
    u.print(Panel(inner, title=title, title_align="left", box=box.ASCII if u.plain else box.ROUNDED, width=u.read_width,
                  padding=(1, 2), border_style="accent"))


def stats(u, course, state, today, weeks=12):
    u.print()
    u.rule(u.t("Stats", "통계"))
    i, into, span = P.level_progress(state["xp"])
    nxt_name = P.LEVELS[i + 1][2 if u.lang == "ko" else 1] if i < len(P.LEVELS) - 1 else None
    done = sum(P.lesson_done(state, l.id) for l in course.lessons)

    def level_row(scale):
        t = Text(f"{i + 1}  ", style="bold")
        t.append(P.level_name(state["xp"], u.lang), style="bold accent"), t.append("  ")
        t.append_text(U.bar_text(into / span * scale, 20, u.plain))
        t.append(f"  {into}/{span}" + (u.t(f" to {nxt_name}", f" → {nxt_name}") if nxt_name else u.t(" top level", " 최고 레벨")), style="muted")
        return t

    def lessons_row(scale):
        t = Text(f"{done}/{len(course.lessons)}  ", style="bold")
        t.append_text(U.bar_text(done / len(course.lessons) * scale, 20, u.plain))
        return t

    xp = Text(str(state["xp"]), style="bold")
    xp.append(" XP", style="muted")
    st = P.streak(state, today)
    names = {p.no: p.title(u.lang) for p in course.phases}
    badges = ", ".join(f"{b[5:]} {names.get(b[5:], '')}".strip() for b in state["badges"]) or u.t("none yet", "아직 없음")
    ans = [v for q in state["q"].values() for v in q.values()]
    got = state["rv"].get(today.isoformat(), 0)
    rows = [("XP", lambda s: xp), (u.t("Level", "레벨"), level_row),
            (u.t("Streak", "연속"), lambda s: Text(f"{st} " + u.t("day" if st == 1 else "days", "일"), style="warn" if st else "muted")),
            (u.t("Badges", "배지"), lambda s: Text(badges, style="" if state["badges"] else "muted")),
            (u.t("Lessons", "레슨"), lessons_row),
            (u.t("Answers", "답"), lambda s: Text(u.t(f"{sum(ans)} right of {len(ans)}", f"{len(ans)}개 중 {sum(ans)}개 정답"))),
            ("Daily 5", lambda s: Text(f"{got}/{P.DAILY_CAP} XP " + u.t("today", "오늘"), style="ok" if got >= P.DAILY_CAP else ""))]

    def build(scale):
        lines = [Text("  " + U.pad(label, 9), style="muted") + fn(scale) for label, fn in rows]
        return Padding(Text("\n").join(lines), (0, 0, 0, 0))
    motion.animate(u, build)
    u.print()
    heat_strip(u, state, today, weeks)


def heat_strip(u, state, today, weeks=12):
    u.rule(u.t(f"Last {weeks} weeks", f"최근 {weeks}주"))
    start = today - dt.timedelta(days=today.weekday() + 7 * (weeks - 1))
    days = set(state["days"])
    cell = {0: ("..", "muted") if u.plain else ("▂ ", "muted"), 1: ("##", "accent") if u.plain else ("▆ ", "accent"),
            2: ("@@", "ok") if u.plain else ("▆ ", "teal")}
    names = [u.t(n, k) for n, k in zip(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"), ("월", "화", "수", "목", "금", "토", "일"))]
    for wd in range(7):
        t = Text("  " + U.pad(names[wd] if wd % 2 == 0 else "", 4), style="muted")
        for wk in range(weeks):
            d = start + dt.timedelta(days=7 * wk + wd)
            if d > today:
                t.append("  ")
                continue
            lvl = 2 if state["rv"].get(d.isoformat(), 0) >= P.DAILY_CAP else 1 if d.isoformat() in days else 0
            t.append(*cell[lvl])
        u.print(t, no_wrap=True, overflow="crop")
    leg = Text("  " + " " * 4)
    leg.append(cell[0][0], style=cell[0][1]), leg.append(u.t(" none   ", " 없음   "), style="muted")
    leg.append(cell[1][0], style=cell[1][1]), leg.append(u.t(" studied   ", " 공부   "), style="muted")
    leg.append(cell[2][0], style=cell[2][1]), leg.append(u.t(" Daily 5 cleared", " Daily 5 완료"), style="muted")
    u.print(leg)
