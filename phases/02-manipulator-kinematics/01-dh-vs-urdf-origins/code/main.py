# 레슨 02/01: 같은 팔을 DH 표(Craig, standard)와 URDF 식 joint origin 으로 적어 FK 가 같은지 비교한다
import numpy as np


def rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1.0]])


def ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])


def rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])


def tr(x, y, z):
    T = np.eye(4)
    T[:3, 3] = [x, y, z]
    return T


def dh_craig(a, alpha, d, th):  # "modified" / proximal: row i holds a_{i-1}, alpha_{i-1}
    return rx(alpha) @ tr(a, 0, 0) @ rz(th) @ tr(0, 0, d)


def dh_standard(a, alpha, d, th):  # "standard" / distal: row i holds a_i, alpha_i
    return rz(th) @ tr(0, 0, d) @ tr(a, 0, 0) @ rx(alpha)


def fk_dh(rows, q, convention, base=None, tool=None):
    """rows: n x 4 of (a, alpha, d, theta_offset). Nothing checks that the table matches the convention."""
    step = {"craig": dh_craig, "standard": dh_standard}[convention]
    T = np.eye(4) if base is None else base
    for (a, al, d, th), qi in zip(rows, q):
        T = T @ step(a, al, d, th + qi)
    return T if tool is None else T @ tool


def fk_urdf(joints, q, tool=None):
    """joints: list of (xyz, rpy). Each joint turns about its own z axis, like a URDF joint with axis 0 0 1."""
    T = np.eye(4)
    for (xyz, (r, p, y)), qi in zip(joints, q):
        T = T @ tr(*xyz) @ rz(y) @ ry(p) @ rx(r) @ rz(qi)
    return T if tool is None else T @ tool


def craig_to_urdf(rows):
    """Rx(alpha) Tx(a) Rz(q) Tz(d) = Trans(Rx(alpha) [a,0,d]) Rx(alpha) Rz(q), so d folds into the origin."""
    if np.any(np.asarray(rows)[:, 3]):  # a theta offset would need a general rotation-to-rpy conversion
        raise ValueError("craig_to_urdf needs theta offsets of 0")
    return [((rx(al)[:3, :3] @ [a, 0, d]), (al, 0.0, 0.0)) for a, al, d, _ in rows]


def craig_to_standard(rows):
    """Shift (a, alpha) up one row. The first pair becomes a fixed base transform."""
    std = [(*rows[i + 1][:2], rows[i][2], rows[i][3]) for i in range(len(rows) - 1)]
    std.append((0.0, 0.0, rows[-1][2], rows[-1][3]))
    return np.array(std), rx(rows[0][1]) @ tr(rows[0][0], 0, 0)


def planar_craig(l1, l2):
    return np.array([[0.0, 0, 0, 0], [l1, 0, 0, 0]]), tr(l2, 0, 0)


def planar_urdf(l1, l2):
    return [((0, 0, 0), (0, 0, 0)), ((l1, 0, 0), (0, 0, 0))], tr(l2, 0, 0)


if __name__ == "__main__":
    rows, tool = planar_craig(0.4, 0.3)
    q = [0.5, 0.8]
    print("craig   ", fk_dh(rows, q, "craig", tool=tool)[:2, 3])
    print("wrong   ", fk_dh(rows, q, "standard", tool=tool)[:2, 3])
    joints, tool = planar_urdf(0.4, 0.3)
    print("urdf    ", fk_urdf(joints, q, tool)[:2, 3])
