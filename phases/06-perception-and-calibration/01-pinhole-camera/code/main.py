# 레슨 06/01: 핀홀 카메라 투영·역투영과 픽셀·깊이 오차가 3D 위치 오차로 바뀌는 크기
import numpy as np


def project(P, fx, fy, cx, cy) -> np.ndarray:
    """Camera-frame points (N,3), z forward, to pixels (N,2): u = fx*x/z + cx."""
    P = np.atleast_2d(np.asarray(P, float))
    if np.any(P[:, 2] <= 0):
        raise ValueError("point is behind the camera (z <= 0)")
    return np.stack([fx * P[:, 0] / P[:, 2] + cx, fy * P[:, 1] / P[:, 2] + cy], axis=1)


def unproject(uv, z, fx, fy, cx, cy) -> np.ndarray:
    """Pixel plus depth z along the optical axis back to a camera-frame point."""
    uv, z = np.atleast_2d(np.asarray(uv, float)), np.asarray(z, float).reshape(-1)
    return np.stack([(uv[:, 0] - cx) * z / fx, (uv[:, 1] - cy) * z / fy, z], axis=1)


def position_error(uv, z, dz, du, fx, fy, cx, cy) -> dict:
    """Where a pixel error du (px, along u) and a depth error dz (m) move the 3D point."""
    uv = np.asarray(uv, float)
    good = unproject(uv, z, fx, fy, cx, cy)[0]
    bad = unproject(uv + [du, 0.0], z + dz, fx, fy, cx, cy)[0]
    d = bad - good
    return {"total": float(np.linalg.norm(d)), "lateral": float(np.linalg.norm(d[:2])), "delta": d}


def lateral_from_depth_error(u, dz, fx, cx) -> float:
    """Sideways shift caused by a depth error alone: dz * (u - cx) / fx (same slope as the ray)."""
    return abs(dz * (u - cx) / fx)


if __name__ == "__main__":
    K = dict(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
    for z in (0.5, 1.0, 2.0, 4.0):
        e = position_error([520.0, 240.0], z, dz=0.01 * z, du=0.5, **K)
        print(f"z={z} m  1% depth + 0.5 px: {e['total'] * 1000:.1f} mm")
