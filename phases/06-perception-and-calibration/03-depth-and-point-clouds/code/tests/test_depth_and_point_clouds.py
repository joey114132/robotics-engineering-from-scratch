# 레슨 06/03 테스트: depth 이미지에서 점군 만들기, voxel 다운샘플, 최소제곱 평면, RANSAC 평면
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_cloud", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

K = dict(fx=150.0, fy=150.0, cx=80.0, cy=60.0)


def angle_deg(n1, n2):
    return np.degrees(np.arccos(np.clip(abs(n1 @ n2), -1, 1)))


def test_constant_depth_image_unprojects_to_a_flat_sheet():
    depth = np.full((120, 160), 2.0)
    P = m.depth_to_points(depth, **K)
    assert P.shape == (120 * 160, 3) and np.allclose(P[:, 2], 2.0)
    assert np.isclose(P[:, 0].min(), (0 - 80) * 2.0 / 150)


def test_invalid_depth_pixels_are_dropped():
    depth = np.full((4, 4), 1.0)
    depth[0, 0], depth[1, 1] = np.nan, 0.0
    assert len(m.depth_to_points(depth, **K)) == 14


def test_voxel_downsample_averages_points_in_a_voxel_and_keeps_distant_ones():
    P = np.array([[0.01, 0.01, 0.01], [0.03, 0.03, 0.03], [0.5, 0.5, 0.5]])
    out = m.voxel_downsample(P, 0.1)
    assert len(out) == 2
    assert any(np.allclose(r, [0.02, 0.02, 0.02]) for r in out)


def test_fit_plane_recovers_a_noiseless_plane():
    rng = np.random.default_rng(0)
    n = np.array([0.0, 0.5, np.sqrt(0.75)])
    a, b = np.cross(n, [1, 0, 0]), np.cross(n, np.cross(n, [1, 0, 0]))
    P = 1.0 * n + rng.uniform(-1, 1, (200, 1)) * a + rng.uniform(-1, 1, (200, 1)) * b
    nf, d = m.fit_plane(P)
    assert angle_deg(nf, n) < 1e-6 and np.isclose(d, 1.0)


def test_ransac_iteration_count_follows_the_probability_formula():
    # N = log(1 - p) / log(1 - w^3): half inliers, 99% success -> 35 iterations
    assert m.ransac_iters(0.5, 0.99) == 35


def test_outliers_tilt_the_least_squares_plane_but_not_the_ransac_plane():
    depth, truth = m.make_scene(seed=1)
    P = m.depth_to_points(depth, **K)
    n_ls, _ = m.fit_plane(P)
    n_rs, _, inl = m.ransac_plane(P, 0.012, 150, seed=0)
    assert angle_deg(n_ls, truth) > 3.0
    assert angle_deg(n_rs, truth) < 1.0
    assert inl.mean() > 0.80


def test_ransac_is_repeatable_for_a_fixed_seed_and_needs_three_points():
    P = m.depth_to_points(m.make_scene(seed=2)[0], **K)
    a, b = m.ransac_plane(P, 0.012, 50, seed=3), m.ransac_plane(P, 0.012, 50, seed=3)
    assert np.array_equal(a[2], b[2])
    with pytest.raises(ValueError, match="3 points"):
        m.ransac_plane(P[:2], 0.01, 10, seed=0)


def test_voxel_downsample_keeps_the_plane_fit():
    P = m.depth_to_points(m.make_scene(seed=3, box=False, flyers=0.0)[0], **K)
    small = m.voxel_downsample(P, 0.05)
    assert len(small) < len(P) / 5
    assert angle_deg(m.fit_plane(small)[0], m.fit_plane(P)[0]) < 1.0


def test_matches_open3d_segment_plane_when_available():
    o3d = pytest.importorskip("open3d")
    P = m.depth_to_points(m.make_scene(seed=1)[0], **K)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(P)
    model, _ = pcd.segment_plane(distance_threshold=0.012, ransac_n=3, num_iterations=150)
    n = np.array(model[:3]) / np.linalg.norm(model[:3])
    assert angle_deg(n, m.ransac_plane(P, 0.012, 150, seed=0)[0]) < 2.0
