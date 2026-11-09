# 레슨 10/02: LIPM 보행자가 목표 속도를 얻도록 다음 발 위치를 deadbeat 로 고른다 (평면)
import numpy as np

G = 9.81


def time_constant(h, g: float = G):
    """Tc = sqrt(h/g), copied from lesson 10/01 so this lesson runs on its own."""
    return np.sqrt(h / g)


def lipm_state(x0, v0, p, t, h, g: float = G):
    """Closed form of x'' = (g/h)(x - p) with the foot fixed at p. Returns (x, v) after t seconds."""
    tc, a = time_constant(h, g), x0 - p
    c, s = np.cosh(t / tc), np.sinh(t / tc)
    return p + a * c + tc * v0 * s, a * s / tc + v0 * c


def next_foot(x, v, v_target, T, h):
    """Foot for the NEXT stance, chosen at touchdown time so that its end speed is exactly v_target.
    Next stance starts at u = x - p. After T the speed is (u/Tc) sinh + v cosh = v_target; solve for u."""
    tc = time_constant(h)
    u = (v_target - v * np.cosh(T / tc)) * tc / np.sinh(T / tc)
    return x - u


def walk(n_steps, T, h, v_target, step_scale=1.0, x0=0.0, v0=0.0, p0=0.0, samples=20):
    """Each stance lasts T. The commanded step length is step_scale * the deadbeat step length."""
    foot, x, v = p0, x0, v0
    feet, t_all, x_all, v_end, x_end = [p0], [], [], [], []
    for k in range(n_steps):
        for t in np.linspace(0, T, samples, endpoint=False):
            t_all.append(k * T + t)
            x_all.append(lipm_state(x, v, foot, t, h)[0])
        x, v = lipm_state(x, v, foot, T, h)
        v_end.append(v)
        x_end.append(x)
        foot = foot + step_scale * (next_foot(x, v, v_target, T, h) - foot)
        feet.append(foot)
    return dict(t=np.array(t_all), x=np.array(x_all), feet=np.array(feet), v_end=np.array(v_end), x_end=np.array(x_end))


if __name__ == "__main__":
    for s in (1.0, 0.6, 1.5):
        r = walk(8, 0.4, 0.9, 0.6, step_scale=s, x0=-0.05, v0=0.3)
        print(s, np.round(r["v_end"], 2), np.round(np.diff(r["feet"]), 2))
