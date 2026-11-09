# 레슨 06/03 그림: RANSAC inlier·outlier 와 최소제곱 평면의 기울어짐을 측면도와 depth 이미지 마스크로 보인다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("cloud_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

K = (150.0, 150.0, 80.0, 60.0)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    depth, truth = m.make_scene(1)
    P = m.depth_to_points(depth, *K)
    n_ls, d_ls = m.fit_plane(P)
    n_rs, d_rs, inl = m.ransac_plane(P, 0.012, 150, seed=0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.25, 1]})
    sub = np.random.default_rng(0).choice(len(P), 2500, replace=False)
    out = sub[~inl[sub]]
    ins = sub[inl[sub]]
    ax1.scatter(P[out, 2], P[out, 1], s=5, color=ORANGE, label="outliers (box, flyers)")
    ax1.scatter(P[ins, 2], P[ins, 1], s=5, color=BLUE, label="RANSAC inliers")
    y = np.linspace(-0.6, 0.6, 2)
    for n, d, color, ls, lab in ((n_ls, d_ls, GREY, "--", "least squares: %.1f deg off" % np.degrees(np.arccos(abs(n_ls @ truth)))),
                                 (n_rs, d_rs, "black", "-", "RANSAC: %.2f deg off" % np.degrees(np.arccos(abs(n_rs @ truth))))):
        ax1.plot((d - n[1] * y) / n[2], y, ls, color=color, lw=2.2, label=lab)
    ax1.set_xlim(0, 3.1)
    ax1.set_ylim(-0.6, 0.7)
    ax1.set_xlabel("depth z (m)")
    ax1.set_ylabel("height y in camera frame (m)")
    ax1.set_title("Side view: least squares is pulled toward the outliers")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(alpha=0.3)
    mask = np.where(inl.reshape(depth.shape), 0, 1)
    ax2.imshow(mask, cmap=matplotlib.colors.ListedColormap([BLUE, ORANGE]), interpolation="nearest")
    ax2.set_title("Image view: box and flyers are outliers")
    ax2.set_xlabel("pixel column u")
    ax2.set_ylabel("pixel row v")
    fig.tight_layout()
    out_png = HERE.parent / "assets" / "fig-cloud-ransac.png"
    out_png.parent.mkdir(exist_ok=True)
    fig.savefig(out_png, dpi=100)
    print(out_png)


if __name__ == "__main__":
    main()
