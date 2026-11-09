# 레슨 09/03: 점-원, 선분-원 정확 검사와 간격을 둔 swept 검사, 터널링을 막는 half-step 패딩
import numpy as np


def in_circle(p, c, r):
    return float(np.linalg.norm(np.asarray(p, float) - c)) <= r


def seg_hits(a, b, c, r):
    """Exact: closest point of segment a-b to the centre c, then compare with r."""
    d = b - a
    L2 = float(d @ d)
    t = 0.0 if L2 == 0 else float(np.clip((c - a) @ d / L2, 0, 1))
    return in_circle(a + t * d, c, r)


def swept_hits(a, b, c, r, step, pad=0.0):
    """Test only points spaced at most `step` apart along a-b. pad grows the circle."""
    n = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
    pts = a + np.linspace(0, 1, n + 1)[:, None] * (b - a)
    return bool((np.linalg.norm(pts - c, axis=1) <= r + pad).any())


def conservative_hits(a, b, c, r, step):
    """Every point of the segment is within step/2 of a sample, so padding by step/2 cannot miss a hit."""
    return swept_hits(a, b, c, r, step, pad=step / 2)


if __name__ == "__main__":
    a, b, c, r = np.array([0.0, 0.0]), np.array([10.0, 0.0]), np.array([5.5, 0.0]), 0.1
    for step in (1.0, 0.4, 0.1):
        print(f"step {step}: exact {seg_hits(a, b, c, r)}  swept {swept_hits(a, b, c, r, step)}  padded {conservative_hits(a, b, c, r, step)}")
