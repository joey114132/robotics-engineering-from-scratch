# 카메라 캘리브레이션 (Camera Calibration)

> 기울인 평면 격자를 몇 장 찍으면 선형 대수만으로 `fx, fy, cx, cy`를 풀 수 있지만 답의 품질은 시점이 얼마나 다양한지에 달려 있습니다.

**유형:** 만들기   **선수 지식:** 06/01 핀홀 카메라   **시간:** 약 15분

## 쉽게 말하면

카메라가 스탠드 위에서 패들에 붙은 체커보드를 봐요. 칸은 전부 크기가 같고 모서리가 직각이어서 사진 속 칸이 찌그러져 보인다면 보드의 기울기와 카메라 렌즈 때문이에요. 보드를 새로 기울이면 칸이 다른 모양으로 찌그러지고 그 모양이 새 단서가 돼요.

기울이지 않고 보드를 밀기만 하면 모양이 그대로여서 단서가 늘지 않아요. 여러 방향으로 기울이면 렌즈가 얼마나 강하게 확대하는지를 나타내는 focal length와 카메라 중심선이 닿는 pixel인 principal point를 풀 수 있어요.

## 문제

datasheet에 적힌 focal length를 믿고 영상 가장자리 pixel을 역투영했더니 점이 몇 cm 어긋납니다. 실제 `fx`와 `cx`는 다른데 영상만 봐서는 알 수 없습니다.
그래서 기하를 아는 타깃으로 직접 재야 합니다.

## 개념

![격자에서 fx, fy, cx, cy까지 선형 4단계](../assets/diagram-calib-steps.png)

*왼쪽에서 오른쪽으로 읽으세요. 시점마다 행렬 `H`가 하나 나오고 `H`들이 행렬 `B`를 주고 `B`가 `fx, fy, cx, cy`를 줍니다.*

보드는 평평해서 각 모서리 점에 `Z = 0`인 보드 좌표 `(X, Y)`를 줄 수 있습니다. 행렬 `K`는 `fx, fy, cx, cy`를 담고 있습니다. 시점 하나마다 `(X, Y, 1)`을 pixel로 보내는 3x3 행렬 `H = K [r1 r2 t]`(homography)가 생깁니다. `r1, r2`는 보드의 두 변 방향이고 `t`는 보드의 위치이므로 `H`의 첫 두 열은 `h1 = K r1`과 `h2 = K r2`입니다.

두 변은 서로 수직이고 길이가 같습니다. `r = K^-1 h`를 대입하면(`'`와 `T`는 전치를 뜻합니다) `h1' B h2 = 0`과 `h1' B h1 = h2' B h2`가 됩니다. 여기서 `B = K^-T K^-1`은 미지수를 모은 행렬이고 시점 하나가 선형 식 두 개를 줍니다.
`B`는 대칭이라 숫자가 여섯 개이고 skew(pixel 격자의 기울어진 정도)가 0이면 하나가 빠집니다. `B`는 배율을 모른 채 구하므로 식 네 개면 충분하고 기울기가 다른 시점 두 장이면 됩니다.

예를 들어 `fx = 620`, `fy = 580`, `cx = 330`, `cy = 235`인 `K`에 `make_views(K, 4, 0.0, 3)`을 쓰면 pixel 잡음 없는 시점 네 장(seed 3)이 만들어집니다. 28도에서 42도까지 기울이면 정확히 그 `K`가 돌아옵니다. 같은 식으로 밀기만 하고 기울이지 않으면 시점마다 같은 단서만 더해지므로 `calibrate()`가 `degenerate views` 예외를 냅니다.

![카메라 두 대 앞의 보드 두 개, 하나는 밀기만 하고 하나는 기울임](../assets/clip-example.mp4)

*파란 보드는 밀기만 하다가 빨간 X로 끝납니다(거부됨). 초록 보드는 매번 다르게 기울이다가 초록 공으로 끝납니다(풀림).*

![쓸 수 있는 시점과 못 쓰는 시점](../assets/diagram-calib-views.png)

*밀기만 하면 같은 단서가 반복되어 거부되고 기울기가 다르면 새 단서가 더해집니다.*

![pixel 잡음에 따른 오차](../assets/fig-calib-noise.png)

*seed를 고정한 100회 실행의 median입니다. 시점이 3장이면 선형 해의 오차가 pixel 잡음의 몇 배가 되고 시점을 늘리면 대략 절반으로 줄어듭니다.*

## 만들기

```python
A = np.array([r for H in Hs for r in (_v(H, 0, 1), _v(H, 0, 0) - _v(H, 1, 1))])
b = np.linalg.svd(A)[2][-1]          # smallest singular vector = [B11, B22, B13, B23, B33]
cx, cy = -B13 / B11, -B23 / B22
fx, fy = np.sqrt(lam / B11), np.sqrt(lam / B22)   # lam = B33 - B13^2/B11 - B23^2/B22
```

`homography_dlt()`는 두 점 집합을 정규화하고 점마다 행을 두 개씩 쌓아 가장 작은 singular vector를 취합니다. `calibrate()`는 퇴화했거나 물리적으로 말이 안 되는 결과에서 예외를 냅니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/02-camera-calibration -q
```

## 실제 도구로 보기

같은 합성 시점에 distortion 항을 고정하고 `cv2.calibrateCamera`를 돌려서 `fx`와 `cy`를 비교합니다. 실제 도구는 이 선형 해를 시작점으로 삼아 reprojection error를 줄이는 비선형 최소제곱으로 다듬습니다.

출처는 [OpenCV 캘리브레이션 튜토리얼](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)(구버전)입니다.

이 문서는 `cv2.calibrateCamera`가 camera matrix, distortion 계수, pose를 돌려준다고 설명하고 reprojection error로 그 결과를 확인합니다.

## 결과물

`outputs/skill-intrinsics-calibration-check.md`는 캘리브레이션 결과를 시점 다양성, 오차 크기, 그럴듯함의 세 가지로 검토합니다.

## 연습 문제

1. zero-skew 가정을 빼고 `B12`를 추가해서 오차가 어떻게 달라지는지 보세요.
2. 잡음 1 px에서 한 번도 실패하지 않는 최소 시점 수를 찾으세요.
3. `scipy.optimize.least_squares`로 비선형 보정 단계를 넣고 오차를 비교하세요.
