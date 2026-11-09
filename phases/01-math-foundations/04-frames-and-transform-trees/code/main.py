# 레슨 01/04: 이름 붙은 frame 트리를 만들고 공통 조상을 거쳐 임의의 두 frame 사이 transform 을 조회한다
import numpy as np


def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def is_rotation(R, tol=1e-9):
    return bool(np.allclose(R.T @ R, np.eye(3), atol=tol) and np.isclose(np.linalg.det(R), 1.0, atol=tol))


def make_T(R, p):
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, p
    return T


def invert_T(T):
    return make_T(T[:3, :3].T, -T[:3, :3].T @ T[:3, 3])


class TFTree:
    """Each frame has one parent. T_parent_child maps coordinates in child into parent."""

    def __init__(self):
        self.parent, self.T = {}, {}

    def add(self, child, parent, T_parent_child):
        if child in self.parent:
            raise ValueError(f"{child} already has a parent")
        node = parent
        while node in self.parent and node != child:
            node = self.parent[node]
        if node == child:
            raise ValueError(f"{child} -> {parent} would make a cycle")
        self.parent[child], self.T[child] = parent, np.asarray(T_parent_child, dtype=float)

    def _up(self, frame):
        if frame not in self.parent and frame not in self.parent.values():
            raise KeyError(frame)
        chain = [frame]
        while chain[-1] in self.parent:
            chain.append(self.parent[chain[-1]])
        return chain

    def _to_ancestor(self, frame, ancestor):
        T = np.eye(4)
        while frame != ancestor:
            T, frame = self.T[frame] @ T, self.parent[frame]
        return T

    def lookup(self, to, frm):
        """T_to_from: walk both frames up to their common ancestor, then go down one side."""
        up_to, up_from = self._up(to), self._up(frm)
        common = next((f for f in up_from if f in up_to), None)
        if common is None:
            raise ValueError(f"{to} and {frm} are in different trees")
        return invert_T(self._to_ancestor(to, common)) @ self._to_ancestor(frm, common)


if __name__ == "__main__":
    t = TFTree()
    t.add("base", "world", make_T(rot_z(0.5), [1, 0, 0]))
    t.add("cam", "base", make_T(rot_y(0.3), [0.2, 0.1, 0.8]))
    t.add("tool", "base", make_T(rot_x(-0.7), [0.4, 0, 0.3]))
    print("T_tool_cam position:", t.lookup("tool", "cam")[:3, 3].round(3))
