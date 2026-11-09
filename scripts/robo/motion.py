# 모션 기반 시설: ease, 켜짐 규칙, 프레임 루프(Live), 하루 한 번 인트로, 막대 채우기
import contextlib
import os
import sys
import time
from datetime import date

from rich.cells import cell_len
from rich.live import Live
from rich.text import Text

from . import progress as P
from . import ui as U

INTRO_SECONDS = 1.2
BAR_SECONDS = 0.5


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_out(x):
    """cubic ease-out: 처음에 빠르고 끝에서 느려진다."""
    return 1 - (1 - clamp01(x)) ** 3


def smoothstep(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def bar_scale(t, dur=BAR_SECONDS):
    return ease_out(t / dur)


def _stdout_isatty():
    return sys.stdout.isatty()


def anim_enabled(u):
    """TTY 이고 색이 있을 때만 움직인다. --plain, NO_COLOR, ROBO_NO_ANIM=1, ROBO_FAST(테스트용)는 끈다."""
    if u.plain or not u.console.is_terminal or not _stdout_isatty():
        return False
    if os.environ.get("NO_COLOR") or os.environ.get("ROBO_NO_ANIM") == "1" or os.environ.get("ROBO_FAST"):
        return False
    return True


@contextlib.contextmanager
def keys():
    """cbreak 로 바꿔 두고 키가 눌렸는지 몰래 확인하는 poll() 을 준다. stdin 이 TTY 가 아니면 항상 False."""
    try:
        import select
        import termios
        import tty
        ok = sys.stdin.isatty()
    except (ImportError, ValueError):
        ok = False
    if not ok:
        yield lambda: False
        return
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)

        def poll():
            if select.select([fd], [], [], 0)[0]:
                os.read(fd, 64)
                return True
            return False

        yield poll
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def run_frames(u, frame_fn, duration=None, fps=15, sleep=time.sleep, now=time.monotonic, poll=None, transient=False, final=None):
    """frame_fn(t) 을 fps 로 그려 제자리에서 갱신한다. 끝나면 "done", 키는 "key", Ctrl-C 는 "interrupt".
    Live 의 with 가 어떤 경우에도 커서를 되돌린다. final 이 있으면 끝에서 그 프레임을 남긴다."""
    reason = "done"
    start = now()
    u.refresh_width()
    with Live(frame_fn(0.0), console=u.console, auto_refresh=False, transient=transient) as live:
        try:
            while True:
                u.refresh_width()                       # 창 크기가 바뀌었으면 레이아웃 폭과 Console 폭을 함께 갱신한다
                t0 = now()
                t = t0 - start
                if duration is not None and t >= duration:
                    break
                live.update(frame_fn(t), refresh=True)
                if poll is not None and poll():
                    reason = "key"
                    break
                sleep(max(0.0, 1.0 / fps - (now() - t0)))
        except KeyboardInterrupt:
            reason = "interrupt"
        if final is not None:
            live.update(final(), refresh=True)
    return reason


def animate(u, build, duration=BAR_SECONDS, fps=30, sleep=time.sleep, now=time.monotonic, enabled=None):
    """build(scale) 을 scale 0 -> 1 (ease-out)로 그린다. 꺼져 있으면 build(1) 을 한 번만 출력한다."""
    if enabled is None:
        enabled = anim_enabled(u)
    if not enabled:
        u.console.print(build(1.0))
        return "disabled"
    return run_frames(u, lambda t: build(ease_out(t / duration)), duration=duration, fps=fps, sleep=sleep, now=now, final=lambda: build(1.0))


# ---- 인트로 ---------------------------------------------------------------------------------------
def _marker():
    return P.progress_path().parent / "last-intro"


def intro_due(today):
    try:
        return _marker().read_text().strip() != today.isoformat()
    except OSError:
        return True


def mark_intro(today):
    try:
        _marker().parent.mkdir(parents=True, exist_ok=True)
        _marker().write_text(today.isoformat() + "\n")
    except OSError:
        pass


def intro_frame(u, hud, t, tagline=None):
    """t 초의 인트로 한 장면(순수 함수). 배너가 왼쪽에서 오른쪽으로 쓸리며 나타나고 부제와 HUD 가 이어서 떠오른다."""
    rows = U.banner_rows()
    w = cell_len(rows[0])
    s = smoothstep(t / 0.8)
    sweep = None if t >= 0.8 else (w + 4) * s - 1
    side = 0 if t < 0.35 else 0.5 if t < 0.6 else 1
    lines = [Text(" ")] + U.banner_lines(u, tagline=tagline, sweep=sweep, side=side) + [Text(" ")]
    if t < 0.8:
        lines.append(Text(" "))
    else:
        h = Text("  ") + hud
        if t < 1.0:
            h.stylize("dim")
        lines.append(h)
    return Text("\n").join(lines)


def play_intro(u, hud, tagline=None, sleep=time.sleep, now=time.monotonic, poll=None, enabled=None):
    """하루에 한 번 도는 인트로. 아무 키나 Ctrl-C 는 건너뛰기이고 마지막 장면은 항상 남는다."""
    if enabled is None:
        enabled = anim_enabled(u)
    if not enabled:
        return "disabled"
    final = lambda: intro_frame(u, hud, INTRO_SECONDS, tagline)
    frame = lambda t: intro_frame(u, hud, min(t, INTRO_SECONDS), tagline)
    if poll is not None:
        return run_frames(u, frame, duration=INTRO_SECONDS, fps=30, sleep=sleep, now=now, poll=poll, final=final)
    with keys() as p:
        return run_frames(u, frame, duration=INTRO_SECONDS, fps=30, sleep=sleep, now=now, poll=p, final=final)
