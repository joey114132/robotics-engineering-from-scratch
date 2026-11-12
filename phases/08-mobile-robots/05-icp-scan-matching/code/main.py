# 레슨 08/05: 최근접점 매칭과 SVD(Kabsch) 강체 맞춤을 반복하는 2D ICP 스캔 정합
import numpy as np

ROOM = np.array([[0, 0], [6, 0], [6, 2], [4, 2], [4, 4], [0, 4], [0, 0]], float)  # an L-shaped room outline


def room(spacing, phase=0.0, poly=ROOM):
    """Points every `spacing` metres along the outline, starting `phase * spacing` into each edge."""
    pts = []
    for a, b in zip(poly[:-1], poly[1:]):
        n = np.linalg.norm(b - a)
        s = np.arange(phase * spacing, n, spacing)
        pts.append(a + s[:, None] * (b - a) / n)
    return np.vstack(pts)


def nearest(A, B):
    """Index into B of the closest point for every point of A."""
    return np.argmin(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1), axis=1)


def kabsch(P, Q):
    """Best rotation R and shift t with R p + t close to q for paired rows: SVD of the cross-covariance."""
    pc, qc = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - pc).T @ (Q - qc))
    D = np.diag([1.0, np.sign(np.linalg.det(Vt.T @ U.T))])  # forbid a mirror image
    R = Vt.T @ D @ U.T
    return R, qc - R @ pc


def icp(src, dst, iters=60, tol=1e-12):
    """Move src onto dst. Returns total R, t and the rms nearest-point error before every iteration and after the last."""
    R, t, cur = np.eye(2), np.zeros(2), src.copy()
    errs = []
    for _ in range(iters):
        match = dst[nearest(cur, dst)]
        errs.append(np.sqrt(((cur - match) ** 2).sum(1).mean()))
        dR, dt = kabsch(cur, match)
        cur, R, t = cur @ dR.T + dt, dR @ R, dR @ t + dt
        if len(errs) > 1 and errs[-2] - errs[-1] < tol:
            break
    errs.append(np.sqrt(((cur - dst[nearest(cur, dst)]) ** 2).sum(1).mean()))
    return R, t, np.array(errs)


if __name__ == "__main__":
    ref, cur = room(0.05, 0.0), room(0.05, 0.5)
    for ang in (0.2, 1.0, 2.6):
        c, s = np.cos(ang), np.sin(ang)
        moved = (cur - [0.3, -0.2]) @ np.array([[c, -s], [s, c]])
        R, t, errs = icp(moved, ref)
        print(f"start rotation {ang} rad: {len(errs) - 1} iterations, final rms {errs[-1]:.3f} m")
