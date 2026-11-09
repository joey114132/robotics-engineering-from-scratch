# 퀴즈를 한 판의 게임처럼: 단계 라벨, 진행 막대, Bolt 반응, 콤보(표시 전용), 별 결과 카드, 완벽할 때 짧은 애니메이션
import os
import random
import sys
import time

from rich.cells import cell_len
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import motion
from . import progress as P
from . import ui as U

STAGES = {"pre": ("Warm-up", "워밍업"), "check": ("Checks", "체크"), "post": ("Boss round", "보스전")}
CHEER = [("Nice one.", "좋아요."), ("Clean.", "깔끔합니다."), ("That is it.", "맞습니다."), ("Gears turning.", "톱니가 잘 맞물립니다.")]
OOPS = [("Close. Read why and it sticks.", "아깝습니다. 이유를 읽으면 기억에 남습니다."),
        ("Not yet. The right answer is shown above.", "아직입니다. 정답은 위에 나와 있습니다."),
        ("Good miss. Now you know why.", "좋은 오답입니다. 이제 이유를 압니다.")]
COMBO_LINES = {3: ("Three in a row.", "3연속입니다."), 5: ("Five straight. On a roll.", "5연속입니다. 기세가 좋습니다.")}


def stars_for(score, total):
    """모두 맞으면 3, ceil(2n/3) 이상이면 2, 아니면 1 (웹사이트와 같은 규칙)."""
    return 3 if score == total else 2 if score >= -(-2 * total // 3) else 1


class Q:
    def __init__(self, text, options, answer, why, stage=None, lesson=None, qi=0):
        self.text, self.options, self.answer, self.why, self.stage, self.lesson, self.qi = text, options, answer, why, stage, lesson, qi


def questions_for(lesson, lang):
    return [Q(q["question"], q["options"], q["answer"], q.get("explanation", ""), q.get("stage"), lesson, i)
            for i, q in enumerate(lesson.quiz(lang))]


# ---- 키 입력 ---------------------------------------------------------------------------
def can_interact(u):
    if u.plain or not sys.stdin.isatty() or not u.console.is_terminal:
        return False
    try:
        import termios  # noqa: F401
    except ImportError:
        return False
    return True


def read_key():
    import select
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = os.read(fd, 1)
        if ch == b"\x1b":
            if select.select([fd], [], [], 0.05)[0]:
                rest = os.read(fd, 2)
                return {b"[A": "up", b"[B": "down", b"OA": "up", b"OB": "down"}.get(rest, "esc")
            return "esc"
        if ch in (b"\r", b"\n"):
            return "enter"
        if ch == b"\x03":
            raise KeyboardInterrupt
        return ch.decode("utf-8", "ignore").lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def ask_line(u, n):
    hint = u.t(f"Type 1-{n} (or a-{chr(96 + n)}), q to stop.", f"1-{n} (또는 a-{chr(96 + n)})을 입력하세요. q 는 중단입니다.")
    while True:
        try:
            raw = input(u.t("answer> ", "답> ")).strip().lower()
        except EOFError:
            return None
        if raw == "q":
            return None
        if raw.isdigit() and 1 <= int(raw) <= n:
            return int(raw) - 1
        if len(raw) == 1 and "a" <= raw <= chr(96 + n):
            return ord(raw) - 97
        u.print(hint, style="muted")


# ---- 그리기 ----------------------------------------------------------------------------
def progress_row(u, outcomes, cur, total, seg=4):
    t = Text("  ")
    if u.plain:
        t.append("[" + " ".join("+" if o is True else "x" if o is False else ">" if i == cur else "." for i, o in enumerate(outcomes + [None] * (total - len(outcomes)))) + "]")
        return t
    for i in range(total):
        o = outcomes[i] if i < len(outcomes) else None
        style = "ok" if o is True else "warn" if o is False else "bold accent" if i == cur else "muted"
        t.append("━" * seg if (o is not None or i == cur) else "─" * seg, style=style)
        t.append(" ")
    return t


def option_lines(u, q, sel, reveal=False, chosen=None):
    """보기 줄들. 긴 보기는 번호 뒤에 맞춰 들여 쓴다(hanging indent)."""
    out = []
    for i, opt in enumerate(q.options):
        if reveal:
            ok_i, bad_i = i == q.answer, i == chosen and i != q.answer
            mark = u.g["good"] if ok_i else u.g["bad"] if bad_i else " "
            head, style, tail_style = f"{mark} {i + 1}  ", ("ok" if ok_i else "warn" if bad_i else "muted"), ("ok" if ok_i else "warn" if bad_i else "muted")
        elif sel is None:                      # 비대화형(입력을 한 줄씩 받는 모드)
            head, style, tail_style = (f"{i + 1}) " if u.plain else f"  {i + 1}  "), "muted", ""
        else:
            on = i == sel
            head, style, tail_style = (u.g["cur"] if on else " ") + f" {i + 1}  ", ("bold accent" if on else "muted"), ("bold" if on else "")
        room = u.read_width - 2 - cell_len(head)
        for k, ln in enumerate(U.wrap_cells(opt, room)):
            t = Text("  ")
            t.append(head if k == 0 else " " * cell_len(head), style=style)
            t.append(ln, style=tail_style)
            out.append(t)
    return out


def options_view(u, q, sel, reveal=False, chosen=None):
    return Text("\n").join(option_lines(u, q, sel, reveal, chosen))


def question_block(u, q, idx, total, outcomes, combo, label):
    w = u.read_width
    if label:
        u.print()
        u.rule(label, w)
    head = Text()
    head.append(u.t(f"Question {idx + 1} of {total}", f"{idx + 1} / {total} 번째 문제"), style="muted")
    u.print()
    u.print(progress_row(u, outcomes, idx, total))
    u.print(Text("  ") + head)
    u.print()
    if q.lesson is not None and q.stage is None:
        u.print(Text(f"  {q.lesson.short}  {q.lesson.title(u.lang)}", style="muted"))
    for line in U.wrap_cells(q.text, w - 4):
        u.print(Text("  " + line, style="bold"))
    u.print()


def feedback(u, q, correct, gained, combo, idx):
    mood = "cheer" if correct else "oops"
    pool = CHEER if correct else OOPS
    phrase = pool[idx % len(pool)]
    if correct and combo in COMBO_LINES:
        phrase = COMBO_LINES[combo]
    phrase = phrase[1] if u.lang == "ko" else phrase[0]
    u.print()
    head = Text("  ")
    if correct:
        head.append(u.g["good"] + " " + u.t("Correct", "정답"), style="bold ok")
        head.append(f"  +{gained} XP" if gained else "  " + u.t("+0 XP (already counted)", "+0 XP (이미 반영됨)"), style="ok" if gained else "muted")
    else:
        head.append(u.g["bad"] + " " + u.t("Not quite", "아쉽습니다"), style="bold warn")
        head.append("  " + u.t("the answer is ", "정답은 ") + f"{q.answer + 1}  {q.options[q.answer]}", style="")
    u.para(head)
    if q.why:
        for i, line in enumerate(U.wrap_cells(q.why, u.read_width - 4)):
            u.print(Text("  " + line, style="muted"))
    u.print()
    face = U.mini_face(mood, u.plain)
    style = "ok" if correct else "warn"
    for i, row in enumerate(face):
        t = Text("  ")
        t.append(row, style=style)
        if i == 1:
            t.append(" " + ("<" if u.plain else "◂") + " ", style="muted")
            t.append(phrase, style="bold " + style if combo < 2 or not correct else "bold")
            if correct and combo >= 2:
                t.append(f"   {u.t('combo', '콤보')} x{combo}", style="bold warn")
        u.para(t)


def celebration_frames(u, n=10, rng=None):
    rng = rng or random.Random(7)
    cols = [u.pal[k] for k in ("accent", "ok", "warn", "teal")]
    sparks = "✦✧▪◦"
    w = 44
    word = u.t("PERFECT", "완벽합니다")
    frames = []
    for f in range(n):
        lines = []
        for r in range(2):
            t = Text("  ")
            for c in range(w):
                t.append(rng.choice(sparks) if rng.random() < 0.16 else " ", style=rng.choice(cols))
            lines.append(t)
        face = U.face_lines("cheer")
        lift = f % 2
        for i in range(6):                       # 얼굴은 6줄 칸 안에서 한 줄 오르내린다(상자가 잘리지 않게)
            row = face[i - lift] if 0 <= i - lift < len(face) else " " * cell_len(face[0])
            t = Text("  " + " " * 14)
            t.append(row, style="bold ok")
            if i == 3 - lift:
                shown = word[: max(1, round(len(word) * (f + 1) / n))]
                t.append("   " + shown, style="bold accent")
            lines.append(t)
        for r in range(2):
            t = Text("  ")
            for c in range(w):
                t.append(rng.choice(sparks) if rng.random() < 0.16 else " ", style=rng.choice(cols))
            lines.append(t)
        frames.append(Text("\n").join(lines))
    return frames


def celebrate(u, sleep=time.sleep):
    if not motion.anim_enabled(u):                  # 켜짐 규칙은 한 곳(motion)에서만 정한다
        return
    frames = celebration_frames(u)
    with Live(frames[0], console=u.console, auto_refresh=False, transient=True) as live:
        for fr in frames:
            live.update(fr, refresh=True)
            sleep(0.11)


def results_panel(u, score, total, gained, state, title, extra_lines=(), shown=3):
    """결과 카드 한 장. shown 개의 별만 켜서 그린다(별 애니메이션의 프레임)."""
    stars = stars_for(score, total)
    verdict = {3: u.t("Perfect round.", "완벽한 한 판입니다."), 2: u.t("Good round.", "좋은 한 판입니다."), 1: u.t("Round done. The misses are worth a re-read.", "한 판 끝났습니다. 틀린 문제는 한 번 더 읽어 보세요.")}[stars]
    st = Text()
    for i in range(3):
        lit = i < stars and i < shown
        st.append(u.g["star"] + " " if lit else u.g["star_off"] + " ", style="bold warn" if lit else "muted")
    body = Text()
    body.append_text(st), body.append("  " + verdict + "\n", style="bold")
    body.append(f"{score}/{total}", style="bold"), body.append(u.t("  correct", "  정답"), style="muted")
    body.append(f"     XP +{gained}", style="bold ok" if gained else "muted")
    body.append(f"  ({u.t('total', '누적')} {state['xp']})", style="muted")
    i, into, span = P.level_progress(state["xp"])
    body.append("\n" + u.t("Level ", "레벨 ") + f"{i + 1} ", style="muted"), body.append(P.level_name(state["xp"], u.lang), style="bold accent")
    body.append("  "), body.append_text(U.bar_text(into / span, 14, u.plain)), body.append(f"  {into}/{span}" if i < len(P.LEVELS) - 1 else "", style="muted")
    for ln in extra_lines:
        body.append("\n"), body.append_text(ln) if isinstance(ln, Text) else body.append(ln, style="muted")
    return Panel(body, title=Text(f" {title} ", style="bold accent"), title_align="left", box=box.ASCII if u.plain else box.ROUNDED,
                 width=u.read_width, padding=(1, 2), border_style="accent")


def results_card(u, score, total, gained, state, title, extra_lines=(), animate=False, sleep=time.sleep):
    """결과 카드. animate 이고 움직임이 켜져 있으면 별이 0.2 초 간격으로 하나씩 켜진다(나머지 내용은 처음부터 보인다)."""
    stars = stars_for(score, total)
    card = lambda shown: results_panel(u, score, total, gained, state, title, extra_lines, shown)
    u.print()
    if not (animate and motion.anim_enabled(u)):
        u.print(card(3))
        return
    with Live(card(0), console=u.console, auto_refresh=False) as live:
        try:
            for k in range(1, stars + 1):
                live.update(card(k), refresh=True)
                sleep(0.2)
        except KeyboardInterrupt:
            live.update(card(3), refresh=True)


class Session:
    def __init__(self, u, questions, award, save, label_stages=True, sleep=time.sleep):
        self.u, self.questions, self.award, self.save, self.label_stages, self.sleep = u, questions, award, save, label_stages, sleep

    def choose(self, q):
        u = self.u
        if not can_interact(u):
            return ask_line(u, len(q.options))
        sel = 0
        with Live(options_view(u, q, sel), console=u.console, auto_refresh=False, transient=True) as live:
            while True:
                k = read_key()
                if k in ("up", "k"):
                    sel = (sel - 1) % len(q.options)
                elif k in ("down", "j"):
                    sel = (sel + 1) % len(q.options)
                elif k.isdigit() and 1 <= int(k) <= len(q.options):
                    sel = int(k) - 1
                    break
                elif k == "enter":
                    break
                elif k in ("q", "esc"):
                    return None
                live.update(options_view(u, q, sel), refresh=True)
        return sel

    def run(self):
        """한 판을 돌린다. (점수, 받은 XP, 끝까지 했는지) 를 돌려준다."""
        u, total = self.u, len(self.questions)
        outcomes, combo, score, gained, last_stage = [], 0, 0, 0, None
        for idx, q in enumerate(self.questions):
            label = None
            if self.label_stages and q.stage and q.stage != last_stage:
                names = STAGES.get(q.stage, (q.stage, q.stage))
                label = names[1] if u.lang == "ko" else names[0]
                last_stage = q.stage
            question_block(u, q, idx, total, outcomes, combo, label)
            if can_interact(u):
                pass
            else:
                for ln in option_lines(u, q, None):
                    u.print(ln)
                u.print()
            pick = self.choose(q)
            if pick is None:
                u.print(Text("  " + u.t("Stopped. Progress so far is saved.", "중단했습니다. 지금까지의 진행은 저장되었습니다."), style="muted"))
                return score, gained, False
            correct = pick == q.answer
            got = self.award(q, correct)
            self.save()
            combo = combo + 1 if correct else 0
            score += correct
            gained += got
            outcomes.append(correct)
            if can_interact(u):
                u.print(options_view(u, q, None, reveal=True, chosen=pick))
            feedback(u, q, correct, got, combo, idx)
            if can_interact(u) and idx < total - 1:
                u.print(Text("  " + u.t("press any key", "아무 키나 누르세요"), style="muted"))
                try:
                    read_key()
                except KeyboardInterrupt:
                    return score, gained, False
        return score, gained, True
