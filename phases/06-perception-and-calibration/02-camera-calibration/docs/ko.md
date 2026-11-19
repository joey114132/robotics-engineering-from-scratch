# 카메라 캘리브레이션 (Camera Calibration)

> 체커보드와 기울여 찍은 몇 장의 사진으로 카메라 자신의 줌과 중심을 재는 법을 배웁니다.

**유형:** 만들기   **선수 지식:** 06/01 핀홀 카메라   **시간:** 약 15분

## 쉽게 말하면

카메라가 체커보드를 봐요. 칸은 모두 크기가 같고 모서리가 직각이라서 사진 속 칸이 찌그러져 보이는 것은 보드의 기울기와 렌즈 때문이에요.

기울기를 바꿀 때마다 새 단서가 돼요. 보드를 기울이지 않고 밀기만 하면 새 단서가 없어요.

## 핵심 용어

- **Calibration**: 아는 표적으로 줌이나 중심 같은 카메라 자신의 값을 재는 일입니다.
- **Intrinsics (`K`)**: 카메라 자신의 줌과 중심 값을 담은 matrix(숫자 표)입니다.
- **Homography (`H`)**: 평평한 보드 위의 한 지점을 pixel로 바꿔 주는 3x3 숫자 표입니다.
- **Degenerate views**: 같은 단서를 되풀이해서 풀 수 없는 시점들입니다.
- **Reprojection error**: 내 값으로 투영한 모서리가 실제로 본 모서리와 얼마나 떨어져 있는지입니다.

## 문제

로봇이 카메라로 본 것을 집으려는데 이미지 가장자리 근처에서 몇 센티미터 빗나갑니다. datasheet의 focal length는 내 카메라의 값이 아니므로 아는 표적으로 직접 재야 합니다.

## 개념

카메라는 저마다 조금씩 달라서 datasheet를 믿는 로봇은 물건의 위치를 잘못 판단합니다.

![선형 네 단계](../assets/diagram-calib-steps.png)

*사진에서 카메라 숫자까지 이어지는 네 단계를 보세요.*

평평한 체커보드는 모서리 위치가 알려져 있습니다. 새 각도에서 찍은 사진마다 그 위치와 pixel을 잇는 식이 나옵니다. 기울기가 다른 사진 두 장이면 간단한 matrix 계산만으로 카메라의 줌과 중심을 풀 수 있습니다.
보드를 밀기만 한 사진은 같은 단서를 되풀이하므로 solver가 거부합니다.

[![밀기만 한 보드와 기울인 보드](../assets/clip-example.jpg)](../assets/clip-example.mp4)

*파란 보드는 밀기만 해서 빨간 십자로 거부됩니다. 초록 보드는 매번 기울여서 초록 공으로 풀립니다.*

![어떤 시점이 통하는가](../assets/diagram-calib-views.png)

*미는 것은 같은 단서를 되풀이하고 기울이면 새 단서가 더해집니다.*

![pixel 노이즈에 따른 오차](../assets/fig-calib-noise.png)

*사진이 적으면 pixel 노이즈의 몇 배 오차가 나옵니다. 사진을 늘리면 오차가 줄어듭니다.*

<details><summary>The math (optional)</summary>

시점마다 보드 모서리 `(X, Y, 1)`을 pixel로 보내는 3x3 `H = K [r1 r2 t]`가 나오고 `K`는 `fx, fy, cx, cy`를 담습니다.
변 `r1, r2`는 서로 수직이고 길이가 같으므로 `B = K^-T K^-1`로 두면 `h1' B h2 = 0`과 `h1' B h1 = h2' B h2`가 성립하고 시점마다 식이 두 개 나옵니다.
`B`는 대칭이라 숫자가 여섯 개이고 zero skew가 하나를 없애며 scale은 모르므로 식 네 개면 충분합니다. 기울인 시점 두 장이면 됩니다.
`fx = 620`, `fy = 580`, `cx = 330`, `cy = 235`일 때 `make_views(K, 4, 0.0, 3)`은 28도에서 42도로 기울어진 시점 4개를 만들고(노이즈 없음, seed 3) 이 시점으로 풀면 정확히 그 `K`가 돌아옵니다.
1 px 노이즈에서 시점을 3장에서 10장으로 늘리면 오차가 대략 절반이 됩니다(100번 실행의 median).

</details>

## 만들기

```python
A = np.array([r for H in Hs for r in (_v(H, 0, 1), _v(H, 0, 0) - _v(H, 1, 1))])
b = np.linalg.svd(A)[2][-1]          # smallest singular vector
B11, B22, B13, B23, B33 = b
cx, cy = -B13 / B11, -B23 / B22
lam = B33 - B13**2 / B11 - B23**2 / B22
fx, fy = np.sqrt(lam / B11), np.sqrt(lam / B22)
```

`homography_dlt()`는 점의 크기를 맞춘 뒤 가장 잘 맞는 값을 찾는 matrix 도구인 SVD를 씁니다. `calibrate()`는 퇴화한 시점과 물리적으로 말이 안 되는 결과를 거부합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/02-camera-calibration -q
```

## 실제 도구로 보기

같은 시점들에서 `cv2.calibrateCamera`와 비교해 보세요.

출처: [OpenCV calibration tutorial](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)(옛 버전)은 `cv2.calibrateCamera`와 reprojection 오차를 설명합니다.

## 결과물

`outputs/skill-intrinsics-calibration-check.md`는 시점이 충분히 다양한지, 오차는 얼마나 큰지, 결과가 말이 되는지 점검합니다.

## 연습 문제

1. `make_views`의 시점 수를 늘리고 오차를 보세요.
2. 모든 시점을 미는 것으로 만들고 거부되는 것을 보세요.
3. pixel 노이즈를 더 주고 시점이 몇 장 필요한지 보세요.
