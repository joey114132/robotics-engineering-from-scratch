# 레슨 11/03: 평면 접촉점의 마찰 원뿔 wrench 를 만들고 볼록 껍질 안쪽 거리(epsilon)로 force closure 를 판정한다
import itertools

import numpy as np


def contact_wrenches(points, normals, mu, rho=1.0):
    """Two edge wrenches (fx, fy, torque / rho) per contact. Normals point into the object."""
    W = []
    for p, n in zip(np.asarray(points, float), np.asarray(normals, float)):
        n = n / np.linalg.norm(n)
        t = np.array([-n[1], n[0]])
        for s in (-1, 1):
            f = n + s * mu * t                      # edge of the friction cone
            W.append([f[0], f[1], (p[0] * f[1] - p[1] * f[0]) / rho])
    return np.array(W)


def epsilon(W, tol=1e-9):
    """Radius of the largest ball around the origin inside the hull of W. 0 means no force closure."""
    W = np.asarray(W, float)
    if np.linalg.matrix_rank(W) < 3:                # the wrenches do not even span the 3-D wrench space
        return 0.0
    h = []
    for i, j, k in itertools.combinations(range(len(W)), 3):
        n = np.cross(W[j] - W[i], W[k] - W[i])
        if np.linalg.norm(n) < tol:
            continue
        n = n / np.linalg.norm(n)
        d = n @ W[i]
        side = W @ n - d
        if np.all(side <= tol):                     # all points behind the plane: a hull facet, outward normal n
            h.append(d)
        elif np.all(side >= -tol):                  # all in front: flip the normal
            h.append(-d)
    return float(max(min(h), 0.0)) if h else 0.0    # origin outside some facet gives a negative distance


def closes(W, tol=1e-9):
    return epsilon(W) > tol


if __name__ == "__main__":
    ang = np.radians([90, 210, 330])
    pts = np.c_[np.cos(ang), np.sin(ang)]
    for mu in (0.0, 0.1, 0.3):
        print(mu, round(epsilon(contact_wrenches(pts, -pts, mu)), 4))
