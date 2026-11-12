# depth와 점군 (Depth and Point Clouds)

> depth 이미지는 역투영을 기다리는 점군입니다. voxel grid로 점을 줄이고 테이블은 RANSAC으로 찾습니다. 단순한 최소제곱 평면은 outlier를 전부 믿기 때문입니다.

**유형:** 만들기   **선수 지식:** 06/01 핀홀 카메라   **시간:** 약 15분

## 쉽게 말하면

자로 책상 표면을 재는데 위에 놓인 책의 높이까지 섞였다고 해 보세요. 모든 측정을 책상이라고 믿고 맞추면 책 쪽으로 기운 평면이 나올 수 있어요.

RANSAC은 무작위로 뽑은 작은 점 묶음으로 평면을 만들고 가까운 점을 세어요. 가장 많은 점이 맞는 평면을 그 점들로 다시 맞춰 책상과 책과 잘못된 depth를 구분해요. 앞 단계의 voxel
grid는 작은 공간 칸마다 점들의 평균을 남겨 point cloud를 줄여요.

## 문제

팔이 물건을 올려놓을 수 있도록 depth 이미지에서 테이블 평면을 맞춥니다. 테이블 위에 상자가 있고 몇몇 픽셀은 엉뚱한 depth를 돌려줍니다.
맞춘 평면이 몇 도 기울고 "수평"이어야 할 놓기 자세가 비스듬해집니다.

## 개념

![depth 이미지에서 테이블 평면까지](../assets/diagram-cloud-pipeline.png)

*유효한 픽셀이 모두 점이 되고 voxel 단계가 점군을 줄이고 RANSAC이 평면과 마스크를 돌려줍니다.*

01번 레슨처럼 각 픽셀을 depth로 역투영합니다. 최소제곱 평면은 거리 제곱을 줄이므로 테이블보다 0.2 m 가까운 상자가 평면을 크게 끌어당깁니다.
RANSAC은 무작위 점 세 개로 평면을 만들고 문턱 안에 드는 점을 세어 가장 좋은 평면을 남깁니다. 필요한 반복 횟수는 `N = log(1 - p) / log(1 - w^3)`입니다. 여기서 `w`는 inlier 비율이고 `p`는 성공 확률입니다.

![RANSAC 한 번의 흐름](../assets/diagram-cloud-ransac.png)

*이긴 평면은 자기 inlier만으로 최소제곱 재적합을 합니다.*

![최소제곱과 RANSAC 비교](../assets/fig-cloud-ransac.png)

*왼쪽은 최소제곱 평면이 상자와 튀는 점 쪽으로 기울고 RANSAC 평면은 테이블을 따라가는 모습입니다. 오른쪽은 outlier가 상자와 엉뚱한 픽셀과 정확히 겹치는 모습입니다.*

## 만들기

```python
key = np.floor(P / size).astype(np.int64)
_, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
n = np.cross(b - a, c - a); n /= np.linalg.norm(n)
inl = np.abs((P - a) @ n) < thr
```

`voxel_downsample()`은 점이 있는 칸마다 평균 점 하나를 만듭니다. `ransac_plane()`은 일직선에 놓인 표본을 건너뛰고 inlier로 재적합합니다.
테스트는 voxel 크기 0.05 m가 점을 5분의 1 아래로 줄이면서 같은 평면을 유지하는 것을 보입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/03-depth-and-point-clouds -q
```

## 실제 도구로 보기

Open3D에는 `PointCloud.voxel_down_sample(voxel_size)`와 `PointCloud.segment_plane(distance_threshold, ransac_n, num_iterations)`가 있고 후자는 평면 계수와 inlier 인덱스를 돌려줍니다.

Open3D가 설치되어 있으면 테스트가 두 법선을 비교합니다.

출처는 [Open3D 점군 튜토리얼](https://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html)이며 두 함수의 이름과 인자를 확인했습니다.

## 결과물

`outputs/skill-plane-fit-check.md`는 평면을 놓기에 쓰기 전에 outlier 민감도를 확인합니다.

## 연습 문제

1. flyer 비율을 올려서 반복 150회의 RANSAC 평면이 실패하기 시작하는 지점을 찾으세요.
2. inlier가 60%일 때 `ransac_iters`로 반복 횟수를 고르세요.
3. 테이블 inlier를 제거한 뒤 상자 윗면을 두 번째 평면으로 맞추세요.
