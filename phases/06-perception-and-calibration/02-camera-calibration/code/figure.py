# 레슨 06/02 그림: 픽셀 잡음에 따른 reprojection 오차와 시점 수에 따른 fx 오차를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("calib_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

K = dict(fx=620.0, fy=580.0, cx=330.0, cy=235.0)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def trial(n, s, i):
    try:
        est = m.calibrate([m.homography_dlt(xy, uv) for xy, uv in m.make_views(K, n, s, i)])
    except ValueError:  # the linear solution can come out unphysical when noise is large and views are few
        return np.nan, np.nan
    return abs(est["fx"] - K["fx"]) / K["fx"] * 100, m.pixel_error(est, K)


def main():
    sig = np.linspace(0, 2, 9)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for n, color in ((3, ORANGE), (10, BLUE)):
        res = np.array([[trial(n, s, i) for i in range(100)] for s in sig])  # (sigma, trial, 2)
        fail = np.isnan(res[:, :, 0]).mean()
        lab = f"{n} views" + (f" ({fail:.0%} of runs failed, not plotted)" if fail else "")
        ax1.plot(sig, np.nanmedian(res[:, :, 1], axis=1), "o-", color=color, lw=2.2, label=lab)
        ax2.plot(sig, np.nanmedian(res[:, :, 0], axis=1), "o-", color=color, lw=2.2, label=lab)
    ax1.plot(sig, sig, "--", color=GREY, lw=1, label="error = noise")
    ax1.set_xlabel("pixel noise sigma (px)")
    ax1.set_ylabel("reprojection error of new points (px)")
    ax1.set_title("Error grows with noise, shrinks with more views")
    ax2.set_xlabel("pixel noise sigma (px)")
    ax2.set_ylabel("error of fx (%)")
    ax2.set_title("The focal length is the hard parameter")
    for ax in (ax1, ax2):
        ax.legend(loc="upper left")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-calib-noise.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
