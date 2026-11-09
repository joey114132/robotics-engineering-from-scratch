# 레슨 04/03: encoder 카운트 양자화와 차분 속도 추정(최소 속도 단계, 창 길이에 따른 노이즈와 지연)
import numpy as np

TWO_PI = 2 * np.pi


def counts(theta, cpr):
    """Integer counts of an encoder with `cpr` counts per revolution (quadrature edges already included)."""
    return np.floor(np.asarray(theta, float) / TWO_PI * cpr).astype(np.int64)


def angle_from_counts(c, cpr):
    return np.asarray(c) * TWO_PI / cpr


def min_velocity_step(cpr, dt):
    """Smallest non-zero velocity a one-sample difference can report: one count per sample."""
    return TWO_PI / cpr / dt


def diff_velocity(c, cpr, dt):
    return np.diff(c) * TWO_PI / cpr / dt


def window_velocity(c, cpr, dt, n):
    """Velocity from counts n samples apart: the step shrinks to step/n, the estimate describes n*dt/2 ago."""
    return (c[n:] - c[:-n]) * TWO_PI / cpr / (n * dt)


def window_lag(n, dt):
    """Time by which an n-sample window estimate trails a signal whose velocity is ramping."""
    return n * dt / 2


if __name__ == "__main__":
    fs, cpr, w0 = 1000.0, 4096, 0.1
    c = counts(w0 * np.arange(int(10 * fs) + 1) / fs, cpr)
    for n in (1, 5, 20):
        v = window_velocity(c, cpr, 1 / fs, n)
        print(n, v.mean(), v.std(), window_lag(n, 1 / fs))
