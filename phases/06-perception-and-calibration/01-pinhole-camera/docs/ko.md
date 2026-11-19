# 핀홀 카메라 (Pinhole Camera)

> 카메라가 컵의 방향은 알려 주지만 거리는 알려 주지 않는 이유와 그 대가를 배웁니다.

**유형:** 만들기   **선수 지식:** 없음   **시간:** 약 15분

## 쉽게 말하면

카메라가 벽 앞에 놓인 컵을 봐요. 컵 가장자리와 벽의 한 점은 같은 시선 위에 있어서 같은 pixel에 찍혀요. pixel은 방향만 알려 주고 거리는 알려 주지 않아요.

그 pixel에 벽의 depth를 쓰면 로봇 팔이 컵을 지나쳐 버려요.

## 핵심 용어

- **Pixel**: 카메라 이미지의 점 하나입니다.
- **Depth (`z`)**: 카메라 앞에서 점까지의 거리입니다.
- **Ray**: pixel을 지나는 시선입니다. 그 위의 모든 점이 같은 pixel에 찍힙니다.
- **Focal length (`fx, fy`)**: 렌즈가 가로와 세로로 얼마나 확대하는지입니다.
- **Principal point (`cx, cy`)**: 카메라의 중심선이 닿는 pixel입니다.
- **Projection**: 3D 점을 pixel로 바꾸는 일입니다.

## 문제

카메라가 컵을 보는데 gripper는 몇 센티미터 옆에서 닫힙니다. depth 값이 가장자리 뒤의 벽에서 왔기 때문입니다.

## 개념

보이는 것을 집으려면 로봇은 pixel을 3D 점으로 바꿔야 하고 그러려면 거리가 필요합니다.

![pixel로 projection하고 depth로 되돌리기](../assets/diagram-pinhole-pipeline.png)

*projection은 3D 점을 pixel로 바꾸고 depth를 잃습니다.*

pixel은 시선 하나일 뿐입니다. 그 시선 위의 모든 점이 같은 pixel에 찍히므로 어느 점을 뜻하는지는 거리가 정합니다. 컵 가장자리 pixel에 벽의 거리를 쓰면 점이 시선을 따라 밀립니다.

[![depth가 너무 큰 컵 두 개](../assets/clip-example.jpg)](../assets/clip-example.mp4)

*두 컵에 같은 거리 실수를 줍니다. 가장자리 컵의 공은 옆으로도 밀립니다.*

![잘못된 depth를 읽는 두 가지 경우](../assets/diagram-pinhole-failure.png)

*depth를 어디서 읽느냐에 따라 pixel이 어느 점에 닿는지 보세요.*

![거리와 pixel 위치에 따른 오차](../assets/fig-pinhole-error.png)

*왼쪽은 오차가 거리에 따라 커지는 모습입니다. 오른쪽은 옆 방향 오차가 가장자리로 갈수록 커지는 모습입니다.*

<details><summary>The math (optional)</summary>

카메라 frame은 `x`가 오른쪽, `y`가 아래, `z`가 앞이므로 `u = fx*x/z + cx`이고 `v = fy*y/z + cy`입니다(`fx, fy`는 pixel 단위). pixel 오차 `du`는 점을 옆으로 `z*du/fx`만큼 움직입니다.
시선은 이미지 중심에서 멀어질수록 비스듬해서 depth 오차 `dz`는 점을 ray를 따라 밀 뿐 아니라 옆으로도 `dz*(u-cx)/fx`만큼 움직입니다. 중심에서는 0이고 이미지 가장자리에서 더 큽니다.
pixel `(520, 240)`, `fx = 600`, `cx = 320`을 예로 듭니다. 컵 가장자리의 depth 1.00 m에서 점은 중심선 오른쪽 0.33 m에 있습니다.
벽의 depth 1.15 m에서는 0.38 m이므로 5 cm 어긋납니다. 그림은 0.5 px와 1% depth 오차, 0.15 m depth 실수를 씁니다.

</details>

## 만들기

```python
def project(P, fx, fy, cx, cy):
    return np.stack([fx*P[:,0]/P[:,2] + cx, fy*P[:,1]/P[:,2] + cy], axis=1)

def unproject(uv, z, fx, fy, cx, cy):
    return np.stack([(uv[:,0]-cx)*z/fx, (uv[:,1]-cy)*z/fy, z], axis=1)
```

`position_error()`는 pixel을 3D 점으로 되돌릴 때 pixel 이동(`du`)과 depth 오차(`dz`)가 있을 때와 없을 때를 비교합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/01-pinhole-camera -q
```

## 실제 도구로 보기

같은 점에서 `project`를 컴퓨터 비전 라이브러리 OpenCV의 `cv2.projectPoints`와 비교해 보세요.

출처: [OpenCV calibration tutorial](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)(옛 버전)은 reprojection 오차에 `cv2.projectPoints`를 씁니다.

## 결과물

`outputs/skill-pixel-depth-check.md`는 pixel과 depth가 같은 표면에 속하는지 확인합니다.

## 연습 문제

1. 렌즈 때문에 상이 휘는 효과(왜곡) 항을 더하세요.
2. 5x5 창의 median으로 depth를 뽑고 그래도 실패하는 곳을 찾으세요.
3. 접어 둔 수학 부분의 pixel 오차와 depth 실수로 2 m 거리에 있는 목표의 옆 방향 오차를 어림해 보세요.
