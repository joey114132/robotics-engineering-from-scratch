# robo 명령줄: 인자 해석, 도움말, 명령 실행
import argparse
import datetime as dt
import math
import os
import random
import re
import shutil
import subprocess
import sys

from rich.cells import cell_len
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from . import data, motion, progress as P, quiz as Qz, scenes, toys, ui as U, views

PROG = "robo"
MIN_COLS = 60
PLAY_RANGES = {"pd-step": {"kp": (0, 1000), "kd": (0, 1000)}, "sampling-limit": {"r": (0.05, 5)}, "kalman": {"q": (0.001, 100), "r": (0.001, 100)}}


def _today():
    """오늘(로컬 달력 날짜). 점수를 줄 때마다 새로 읽어서 자정을 넘겨도 날짜가 맞는다."""
    return dt.date.today()


def _stdout_isatty():
    return sys.stdout.isatty()


def _term_columns():
    return U.term_columns()


def _narrow_notice(width_override):
    if width_override is None and _stdout_isatty() and _term_columns() < MIN_COLS:
        print(f"{PROG}: needs at least {MIN_COLS} columns, output may wrap", file=sys.stderr)


def _validate_play(args, parsers):
    for name, (lo, hi) in PLAY_RANGES[args.toy].items():
        v = getattr(args, name)
        if v is not None and not (math.isfinite(v) and lo <= v <= hi):
            parsers["play"].error(f"argument --{name}: must be a number between {lo:g} and {hi:g} for {args.toy}")
    for name in ("kp", "kd", "r", "q"):
        v = getattr(args, name, None)
        if v is not None and not math.isfinite(v):
            parsers["play"].error(f"argument --{name}: must be a finite number")
COMMANDS = [
    ("home", "", "Progress, level and the next lesson (the default).", "진행 상황, 레벨, 다음 레슨 보기 (기본 화면)."),
    ("map", "", "All lessons by phase, with done and next markers.", "phase별 전체 레슨과 완료, 다음 레슨 표시."),
    ("read", "<lesson>", "Read a lesson with figures, code and Bolt.", "그림, 코드, Bolt와 함께 레슨 읽기."),
    ("quiz", "<lesson>", "A six-question game round for the lesson.", "레슨의 여섯 문제를 한 라운드 게임으로 풀기."),
    ("mission", "<lesson> [--done]", "Show the lesson mission, or tick it for +20 XP.", "레슨 미션 보기. --done을 붙이면 완료로 표시(+20 XP)."),
    ("daily", "", "Daily 5: five review questions, +5 XP each, 25 XP a day.", "오늘의 5문제: 복습 문제 5개, 문제당 +5 XP, 하루 최대 25 XP."),
    ("scene", "[NN]", "A looping terminal animation for a phase (02, 03, 05, 08, 09, 14 have their own).", "phase별 반복 터미널 애니메이션 (02, 03, 05, 08, 09, 14는 전용 장면이 있음)."),
    ("play", "<toy>", "Terminal toys: pd-step, sampling-limit, kalman.", "터미널에서 돌려 보는 toy: pd-step, sampling-limit, kalman."),
    ("stats", "", "XP, level, streak, badges and a 12-week strip.", "XP, 레벨, 연속 학습일, 배지, 12주 달력."),
    ("sync", "export | import <code>", "Move progress between the CLI and the website.", "진행 상황을 CLI와 웹사이트 사이에서 옮기기."),
    ("completion", "bash | zsh", "Print a shell completion script.", "셸 자동완성 스크립트 출력."),
]
HELP_KO = {
    "Language of lessons and screens (default: from $LANG).": "레슨과 화면 언어 (기본값은 $LANG).",
    "No colour, no animation, ASCII frames. Also used when piped or NO_COLOR is set.": "색과 애니메이션 없이 ASCII 테두리로 출력합니다. 파이프로 넘기거나 NO_COLOR가 설정되어 있어도 이렇게 출력합니다.",
    "Print everything at once instead of paging long output through less.": "긴 출력을 less로 나눠 보여 주지 않고 한꺼번에 출력합니다.",
    "Lesson id like 03-02, or part of its name like gravity.": "레슨 id (03-02) 또는 이름 일부 (gravity).",
    "Figure drawing: quad (compact, at most 16 rows), half (compact half blocks), full (terminal width, large), off (caption lines).": "그림 표시 방식: quad(작게, 최대 16줄), half(반블록, 작게), full(터미널 폭에 맞춰 크게), off(캡션 줄만 표시).",
    "Tick the mission (+20 XP, once).": "미션을 완료로 표시합니다 (+20 XP, 한 번만).",
    "Seed for the random picks (for repeatable rounds).": "무작위 선택에 쓰는 seed (같은 라운드를 다시 만들 때).",
    "Phase number 00-16 (default: the phase of your next lesson).": "phase 번호 00-16 (기본값은 다음 레슨의 phase).",
    "Which toy to run.": "실행할 toy.",
    "Proportional gain (pd-step, default 30).": "비례 gain (pd-step, 기본 30).",
    "Derivative gain (pd-step, default 4).": "미분 gain (pd-step, 기본 4).",
    "r = dt*kd/J for sampling-limit (default 0.6, range 0.1-2.5), or sensor sigma for kalman (default 2.0).": "sampling-limit에서는 r = dt*kd/J (기본 0.6, 범위 0.1-2.5), kalman에서는 센서 sigma (기본 2.0).",
    "Process noise sigma the Kalman filter believes (default 0.1).": "칼만 필터가 믿는 process noise sigma (기본 0.1).",
    "export prints a code, import merges a code.": "export는 코드를 출력하고 import는 코드를 합칩니다.",
    "The code printed by export (or by the website).": "export(또는 웹사이트)가 출력한 코드.",
    "Shell to print the script for.": "스크립트를 출력할 셸.",
}


def _add_common(p, top):
    d = {} if top else {"default": argparse.SUPPRESS}
    p.add_argument("--lang", choices=("en", "ko"), help="Language of lessons and screens (default: from $LANG).", **({"default": None} if top else d))
    p.add_argument("--plain", action="store_true", help="No colour, no animation, ASCII frames. Also used when piped or NO_COLOR is set.", **d)
    p.add_argument("--no-pager", action="store_true", help="Print everything at once instead of paging long output through less.", **d)
    p.add_argument("--width", type=int, help=argparse.SUPPRESS, **({"default": None} if top else d))
    p.add_argument("-h", "--help", action="store_true", help=argparse.SUPPRESS, **d)


def build_parser():
    top = argparse.ArgumentParser(prog=PROG, add_help=False)
    _add_common(top, True)
    sub = top.add_subparsers(dest="cmd")
    P_ = {"": top}
    for name, _, _, _ in COMMANDS + [("ids", "", "", "")]:
        P_[name] = sub.add_parser(name, add_help=False)
        _add_common(P_[name], False)
    for n in ("read", "quiz", "mission"):
        P_[n].add_argument("lesson", help="Lesson id like 03-02, or part of its name like gravity.")
    P_["read"].add_argument("--figures", choices=("quad", "half", "full", "off"), default="quad", help="Figure drawing: quad (compact, at most 16 rows), half (compact half blocks), full (terminal width, large), off (caption lines).")
    P_["mission"].add_argument("--done", action="store_true", help="Tick the mission (+20 XP, once).")
    P_["daily"].add_argument("--seed", type=int, help="Seed for the random picks (for repeatable rounds).")
    P_["scene"].add_argument("phase", nargs="?", help="Phase number 00-16 (default: the phase of your next lesson).")
    P_["play"].add_argument("toy", choices=sorted(toys.TOYS), help="Which toy to run.")
    P_["play"].add_argument("--kp", type=float, help="Proportional gain (pd-step, default 30).")
    P_["play"].add_argument("--kd", type=float, help="Derivative gain (pd-step, default 4).")
    P_["play"].add_argument("--r", type=float, help="r = dt*kd/J for sampling-limit (default 0.6, range 0.1-2.5), or sensor sigma for kalman (default 2.0).")
    P_["play"].add_argument("--q", type=float, help="Process noise sigma the Kalman filter believes (default 0.1).")
    P_["play"].add_argument("--seed", type=int, default=1, help="Seed for the random picks (for repeatable rounds).")
    P_["sync"].add_argument("action", choices=("export", "import"), help="export prints a code, import merges a code.")
    P_["sync"].add_argument("code", nargs="?", help="The code printed by export (or by the website).")
    P_["completion"].add_argument("shell", choices=("bash", "zsh"), help="Shell to print the script for.")
    return top, P_


# ---- 도움말 ----------------------------------------------------------------------------
def _flag_label(a):
    names = ", ".join(a.option_strings) if a.option_strings else a.dest.upper() if not a.choices else "{" + ",".join(a.choices) + "}"
    if a.option_strings and a.nargs != 0 and not isinstance(a, argparse._StoreTrueAction):
        names += " " + (("{" + ",".join(a.choices) + "}") if a.choices else a.dest.upper())
    return names


def print_help(u, parsers, cmd):
    w = u.read_width
    if not cmd:
        U.print_banner(u, tagline=u.t("a course reader and tutor for the terminal", "터미널에서 읽고 풀어 보는 코스 리더 겸 튜터"))
        u.print(Text("  ") + Text(u.t("Usage", "사용법"), style="bold") + Text(f"   {PROG} [command] [options]", style="accent"))
        u.print()
        u.rule(u.t("Commands", "명령"), w)
        u.columns([[(name, "bold accent"), (args, "muted"), (ko if u.lang == "ko" else en, "")] for name, args, en, ko in COMMANDS])
        u.print()
        _print_options(u, parsers[""], w)
        u.print(Text("  " + u.t(f"Needs a terminal at least {MIN_COLS} columns wide; a narrower one may wrap the output.",
                                f"터미널 폭이 {MIN_COLS} columns 이상이어야 합니다. 더 좁으면 출력이 줄바꿈될 수 있습니다."), style="muted"))
        u.print()
        u.rule(u.t("Examples", "예시"), w)
        for line in ("robo read 03-02", "robo quiz 03-02", "robo daily", "robo play pd-step --kp 30 --kd 8", "robo sync export"):
            u.print(Text("  " + line, style="accent"))
        u.print()
        u.print(Text("  " + u.t("Completion: ", "자동완성: "), style="muted") + Text('eval "$(robo completion bash)"', style="accent") + Text("   (zsh: robo completion zsh)", style="muted"))
        u.print(Text("  " + u.t("Alias: ", "별칭: "), style="muted") + Text(f"alias robo='python3 {os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'robo.py'))}'", style="accent"), overflow="fold")
        return
    spec = next(c for c in COMMANDS if c[0] == cmd)
    u.print()
    u.print(Text("  ") + Text(f"{PROG} {cmd}", style="bold accent") + Text(f" {spec[1]}", style="muted"))
    u.print(Text("  " + (spec[3] if u.lang == "ko" else spec[2])))
    u.print()
    _print_options(u, parsers[cmd], w, positionals=True)


def _print_options(u, p, w, positionals=False):
    acts = [a for a in p._actions if a.help != argparse.SUPPRESS and a.dest not in ("cmd",)]
    pos = [a for a in acts if not a.option_strings]
    opt = [a for a in acts if a.option_strings]
    if not positionals:
        pos = []
    for title, group in ((u.t("Arguments", "인자"), pos), (u.t("Options", "옵션"), opt)):
        if not group:
            continue
        u.rule(title, w)
        rows = [[(_flag_label(a), "bold accent"), (HELP_KO.get(a.help or "", a.help or "") if u.lang == "ko" else (a.help or ""), "")] for a in group]
        if not positionals and group is opt:
            rows.append([("-h, --help", "bold accent"), (u.t("Show help. Also: robo <command> --help.", "도움말을 보여 줍니다. robo <명령> --help로도 볼 수 있습니다."), "")])
        u.columns(rows)
        u.print()


# ---- 자동완성 ----------------------------------------------------------------------------
BASH = r'''_robo() {
  local cur="${COMP_WORDS[COMP_CWORD]}" prev="${COMP_WORDS[COMP_CWORD-1]}"
  case "$prev" in
    read|quiz|mission) COMPREPLY=($(compgen -W "$(robo ids 2>/dev/null)" -- "$cur")) ;;
    play) COMPREPLY=($(compgen -W "pd-step sampling-limit kalman" -- "$cur")) ;;
    sync) COMPREPLY=($(compgen -W "export import" -- "$cur")) ;;
    --lang) COMPREPLY=($(compgen -W "en ko" -- "$cur")) ;;
    *) COMPREPLY=($(compgen -W "%s --lang --plain --no-pager --help" -- "$cur")) ;;
  esac
}
complete -F _robo robo
'''
ZSH = r'''#compdef robo
_robo() {
  local -a cmds
  cmds=(
@@CMDS@@
  )
  case "$words[CURRENT-1]" in
    read|quiz|mission) compadd -- ${(f)"$(robo ids 2>/dev/null)"} ;;
    play) compadd pd-step sampling-limit kalman ;;
    sync) compadd export import ;;
    --lang) compadd en ko ;;
    *) _describe 'command' cmds; compadd -- --lang --plain --no-pager --help ;;
  esac
}
compdef _robo robo
'''


def zsh_script():
    # _describe 는 '이름:설명' 항목을 받으므로 이름과 설명을 따로 만들고 설명 안의 콜론과 따옴표는 이스케이프한다
    esc = lambda t: t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "'\\''")
    return ZSH.replace("@@CMDS@@", "\n".join(f"    '{name}:{esc(en.rstrip('.'))}'" for name, _, en, _ in COMMANDS))


# ---- 페이저 ----------------------------------------------------------------------------------
def with_pager(u, args, fn):
    if args.no_pager or not sys.stdout.isatty() or not u.console.is_terminal:
        return fn()
    with u.console.capture() as cap:
        fn()
    text = cap.get()
    height = shutil.get_terminal_size((100, 24)).lines
    less = shutil.which("less")
    if text.count("\n") < height - 1 or not less:
        sys.stdout.write(text)
        return
    try:
        env = dict(os.environ, LESSCHARSET="utf-8")
        subprocess.run([less, "-R", "-X", "-F"], input=text.encode("utf-8"), env=env)
    except (OSError, BrokenPipeError):
        sys.stdout.write(text)


# ---- 명령들 ------------------------------------------------------------------------------------
def _err(u, msg):
    print(f"{PROG}: {msg}", file=sys.stderr)
    return 2


def _lesson(course, u, key):
    try:
        return course.resolve(key)
    except LookupError as e:
        _err(u, str(e))
        return None


def cmd_quiz(u, course, state, today, les):
    path = P.progress_path()

    def save():
        P.save(state, path)

    def award(q, correct):
        return P.answer(state, les.id, q.qi, correct, _today())

    while True:
        qs = Qz.questions_for(les, u.lang)
        u.print()
        u.print(Text("  ") + Text(f"{les.short}  ", style="muted") + Text(les.title(u.lang), style="bold accent") + Text("   quiz", style="muted"))
        score, gained, finished = Qz.Session(u, qs, award, save).run()
        if not finished:
            return 1
        new_badges = P.award_badges(state, course.phase_ids)
        save()
        if score == len(qs):
            Qz.celebrate(u)
        extra = []
        if P.lesson_done(state, les.id):
            extra.append(Text(u.g["good"] + " " + u.t("Lesson complete.", "레슨 완료."), style="ok"))
        else:
            left = []
            if len(state["q"].get(les.id, {})) < P.QUESTIONS_PER_LESSON:
                left.append(u.t("answer every question", "모든 문제에 답하기"))
            if not state["m"].get(les.id):
                left.append(f"robo mission {les.short} --done")
            extra.append(Text(u.t("To finish this lesson: ", "레슨을 끝내려면: ") + ", ".join(left), style="muted"))
        for b in new_badges:
            extra.append(Text(u.g["star"] + " " + u.t(f"Badge earned: phase {b[5:]}", f"phase {b[5:]} 배지 획득"), style="bold warn"))
        Qz.results_card(u, score, len(qs), gained, state, u.t("Results", "결과"), extra, animate=True)
        u.print()
        try:
            again = input(u.t("Play again? Replays award no extra XP. [y/N] ", "한 라운드 더 할까요? 다시 풀어도 XP는 늘지 않습니다. [y/N] ")).strip().lower()
        except EOFError:
            again = "n"
        if again not in ("y", "yes", "예", "네"):
            return 0


def cmd_daily(u, course, state, today, seed):
    path = P.progress_path()
    rng = random.Random(seed)
    ids = P.daily_lessons(state, [l.id for l in course.lessons])
    by_lesson = {i: Qz.questions_for(course.by_id(i), u.lang) for i in ids}
    order = list(ids)
    rng.shuffle(order)
    picked = []
    for lid in order:                        # 레슨마다 하나씩 먼저 뽑아 고루 섞는다
        if len(picked) < P.DAILY_COUNT and by_lesson[lid]:
            picked.append(rng.choice(by_lesson[lid]))
    rest = [q for lid in order for q in by_lesson[lid] if q not in picked]
    rng.shuffle(rest)
    picked += rest[:P.DAILY_COUNT - len(picked)]
    for q in picked:
        q.stage = None
    got = P.daily_remaining(state, today)
    spent = P.DAILY_CAP - got
    u.print()
    t = Text(u.t("  Daily 5", "  오늘의 5문제"), style="bold accent")
    t.append(u.t(f"   {spent}/{P.DAILY_CAP} XP today", f"   오늘 {spent}/{P.DAILY_CAP} XP"), style="ok" if got == 0 else "muted")
    u.print(t)
    if got == 0:
        u.print(Text("  " + u.t("Today's 25 XP are already earned, so this round is practice only.", "오늘의 25 XP를 이미 받았으므로 이번 라운드는 연습입니다."), style="muted"))

    def award(q, correct):
        return P.daily_award(state, correct, _today())

    score, gained, finished = Qz.Session(u, picked, award, lambda: P.save(state, path), label_stages=False).run()
    if not finished:
        return 1
    Qz.results_card(u, score, len(picked), gained, state, u.t("Daily 5", "오늘의 5문제"),
                    animate=True, extra_lines=[Text(u.t(f"Today {P.DAILY_CAP - P.daily_remaining(state, _today())}/{P.DAILY_CAP} XP", f"오늘 {P.DAILY_CAP - P.daily_remaining(state, _today())}/{P.DAILY_CAP} XP"), style="muted")])
    if score == len(picked):
        Qz.celebrate(u)
    return 0


def cmd_scene(u, args, course, state):
    key = args.phase
    if key is None:
        nxt = course.next_lesson(state, P.lesson_done)
        ph = int(nxt.phase.no) if nxt else 2
    elif re.fullmatch(r"\d{1,2}", key) and int(key) <= 16:
        ph = int(key)
    else:
        return _err(u, "scene: phase must be a number from 00 to 16")
    name, near = scenes.scene_for_phase(ph)
    phase = next((p for p in course.phases if int(p.no) == ph), None)
    title, title_ko = scenes.INFO[name][0], scenes.INFO[name][1]
    u.print()
    head = Text("  ")
    head.append(f"Phase {ph:02d}", style="bold accent")
    if phase:
        head.append("  " + phase.title(u.lang), style="bold")
    head.append("   " + u.t(title, title_ko), style="muted")
    u.print(head, no_wrap=True, overflow="crop")
    if near is not None:
        u.para(Text(u.t(f"No scene for phase {ph:02d}; showing the nearest, phase {near:02d}.", f"phase {ph:02d}에는 전용 장면이 없어 가장 가까운 phase {near:02d}의 장면을 보여 줍니다."), style="muted"))
    if motion.anim_enabled(u):
        scenes.run_scene(u, name, ph)
        if u.below_min:                                  # 실행 중 터미널이 60 columns 아래로 줄었다
            print(f"{PROG}: needs at least {MIN_COLS} columns, output may wrap", file=sys.stderr)
        return 0
    for line in scenes.scene_lines(u, name, scenes.STATIC_T[name], ph):
        u.print(line, no_wrap=True, overflow="crop")
    u.para(scenes.caption_text(u, name, ph, hint=False))
    return 0


def cmd_sync(u, args, state):
    if args.action == "export":
        u.print(Text(u.t('Paste this code on the website home page, in the "Take your progress along" panel, button "Paste progress code". Or run robo sync import <code>.',
                         '웹사이트 첫 화면의 "진행 상황 옮기기" 패널에서 "진행 코드 붙여넣기" 버튼을 눌러 이 코드를 붙여 넣으세요. 또는 robo sync import <코드>를 실행하세요.'), style="muted"))
        u.console.print(P.export_code(state), soft_wrap=True, markup=False, highlight=False)
        return 0
    if not args.code:
        return _err(u, "sync import needs a code")
    try:
        other = P.import_code(args.code)
    except ValueError:
        return _err(u, f"that progress code is too long (over {P.MAX_CODE_LEN} characters)" if len(args.code) > P.MAX_CODE_LEN else "that is not a progress code")
    merged = P.merge(state, other)
    P.save(merged, P.progress_path())
    n_q = sum(len(v) for v in merged["q"].values()) - sum(len(v) for v in state["q"].values())
    u.print(Text(u.g["good"] + " " + u.t(f"Merged. XP {state['xp']} -> {merged['xp']}, {max(n_q, 0)} new answers, {len(merged['days']) - len(state['days'])} new days.",
                                          f"합쳤습니다. XP {state['xp']} -> {merged['xp']}, 새로 푼 문제 {max(n_q, 0)}개, 새 학습일 {len(merged['days']) - len(state['days'])}일."), style="ok"))
    return 0


def dispatch(args, u):
    course = data.load_course()
    state = P.load()
    today = _today()
    cmd = args.cmd or "home"
    if cmd == "home":
        head = True
        if motion.anim_enabled(u) and motion.intro_due(today):
            motion.mark_intro(today)
            head = motion.play_intro(u, views.hud(u, state, today), views.home_tagline(u, course)) == "disabled"
        views.home(u, course, state, today, head=head)
    elif cmd == "scene":
        return cmd_scene(u, args, course, state)
    elif cmd == "ids":
        print("\n".join(l.short for l in course.lessons))
    elif cmd == "map":
        with_pager(u, args, lambda: views.lesson_map(u, course, state))
    elif cmd == "stats":
        views.stats(u, course, state, today)
    elif cmd == "completion":
        names = " ".join(c[0] for c in COMMANDS)
        print((BASH % names) if args.shell == "bash" else zsh_script())
    elif cmd == "play":
        toys.play(u, args.toy, kp=args.kp, kd=args.kd, r=args.r, q=args.q, seed=args.seed)
    elif cmd == "sync":
        return cmd_sync(u, args, state)
    elif cmd == "daily":
        return cmd_daily(u, course, state, today, args.seed)
    else:
        les = _lesson(course, u, args.lesson)
        if les is None:
            return 2
        if cmd == "read":
            from . import reader  # rich.markdown 과 pygments 는 read 에서만 쓰므로 여기서 불러 다른 명령의 시작을 줄인다
            mode = reader.figures.choose_mode(u.plain, u.console.color_system, args.figures)
            with_pager(u, args, lambda: reader.print_lesson(u, les, state, mode, course.root))
        elif cmd == "mission":
            if args.done:
                gained = P.mission(state, les.id, _today())
                new = P.award_badges(state, course.phase_ids)
                P.save(state, P.progress_path())
                u.print()
                u.print(Text("  " + (u.g["good"] + " " + u.t(f"Mission ticked. +{gained} XP", f"미션을 완료로 표시했습니다. +{gained} XP") if gained else u.t("Already ticked, so +0 XP.", "이미 완료로 표시했으므로 +0 XP.")), style="ok" if gained else "muted"))
                for b in new:
                    u.print(Text("  " + u.g["star"] + " " + u.t(f"Badge earned: phase {b[5:]}", f"phase {b[5:]} 배지 획득"), style="bold warn"))
            else:
                u.print()
                views.mission_card(u, les, state)
        elif cmd == "quiz":
            return cmd_quiz(u, course, state, today, les)
    return 0


def main(argv=None):
    try:
        return _main(argv)
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())      # robo ... | head 처럼 읽는 쪽이 먼저 닫은 경우
        return 0


def _main(argv):
    top, parsers = build_parser()
    argv = sys.argv[1:] if argv is None else argv
    if "-h" in argv or "--help" in argv:       # 필수 인자가 빠져도 도움말은 나와야 한다
        cmd = next((a for a in argv if a in parsers), "")
        lang = next((argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "--lang"), None) or data.default_lang()
        plain = U.want_plain("--plain" in argv, sys.stdout.isatty())
        _narrow_notice(None)
        print_help(U.make_ui(plain=plain, lang=lang if lang in ("en", "ko") else "en"), parsers, cmd)
        return 0
    try:
        args = top.parse_args(argv)
        if args.cmd == "play":
            _validate_play(args, parsers)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    lang = args.lang or data.default_lang()
    plain = U.want_plain(args.plain, sys.stdout.isatty())
    force = bool(os.environ.get("FORCE_COLOR")) and not args.plain and not os.environ.get("NO_COLOR")
    u = U.make_ui(plain=plain and not force, width=args.width, force_color=force, lang=lang)
    _narrow_notice(args.width)
    try:
        return dispatch(args, u)
    except KeyboardInterrupt:
        print()
        return 130
    except BrokenPipeError:
        pass
    finally:
        try:
            sys.stdout.flush()
        except BrokenPipeError:                  # robo ... | head 처럼 읽는 쪽이 먼저 닫은 경우
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return 0
