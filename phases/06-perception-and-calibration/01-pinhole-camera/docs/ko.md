# 핀홀 카메라 (Pinhole Camera)

> 픽셀은 하나의 광선입니다. depth가 그 위의 점을 정하므로 depth가 틀리면 점이 광선을 따라 밀리고 오차는 거리에 비례해 커집니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3)   **시간:** 약 15분

## 문제

비전 시스템이 컵을 픽셀 (520, 240)에 있다고 알려 주고 planner가 그 점으로 팔을 뻗습니다. 그런데 gripper는 옆으로 몇 cm 어긋난 곳을 잡습니다.
픽셀은 컵 가장자리에 있었지만 depth 값은 뒤쪽 테이블에서 읽혔기 때문에, 3D 점이 시선 광선을 따라 미끄러진 것입니다.

## 개념

![픽셀로 투영하고 depth로 되돌리기](../assets/diagram-pinhole-pipeline.png)

*투영은 `z`로 나누면서 depth를 버립니다. 점을 되살리려면 depth가 필요합니다.*

픽셀 단위 focal length `fx, fy`와 principal point `cx, cy`를 쓰면 `u = fx*x/z + cx`이고 `v = fy*y/z + cy`입니다.

픽셀 오차 `du`는 점을 옆으로 `z*du/fx`만큼 움직입니다. depth 오차 `dz`는 점을 광선을 따라 움직이고 영상 중심에서 멀수록 옆으로 `dz*(u-cx)/fx`만큼 벗어납니다.

![틀린 depth를 읽는 두 가지 경우](../assets/diagram-pinhole-failure.png)

*같은 픽셀도 depth를 어디서 읽었는지에 따라 좋은 목표가 되기도 하고 나쁜 목표가 되기도 합니다.*

![거리와 픽셀 위치에 따른 오차](../assets/fig-pinhole-error.png)

*왼쪽은 0.5 px 오차와 1% depth 오차가 모두 거리에 비례하는 모습입니다. 오른쪽은 0.15 m 멀리 읽은 depth가 영상 중심에서 멀수록 옆 오차를 더 크게 만드는 모습입니다.*

## 만들기

```python
def project(P, fx, fy, cx, cy):
    return np.stack([fx*P[:,0]/P[:,2] + cx, fy*P[:,1]/P[:,2] + cy], axis=1)

def unproject(uv, z, fx, fy, cx, cy):
    return np.stack([(uv[:,0]-cx)*z/fx, (uv[:,1]-cy)*z/fy, z], axis=1)
```

`position_error()`는 `du`와 `dz`를 넣은 경우와 뺀 경우로 픽셀을 두 번 역투영해서 그 차이를 돌려줍니다. `project()`는 `z <= 0`이면 예외를 냅니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/01-pinhole-camera -q
```

## 실제 도구로 보기

같은 점에 대해 회전 0, 이동 0, 왜곡 없음으로 `project`와 `cv2.projectPoints`를 비교합니다. OpenCV가 없으면 이 테스트는 건너뜁니다.

출처는 [OpenCV 캘리브레이션 튜토리얼](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)(구버전)입니다.
이 문서는 `cv2.projectPoints`로 reprojection error를 계산합니다.

## 결과물

`outputs/skill-pixel-depth-check.md`는 픽셀과 depth가 같은 표면에서 나왔는지 확인합니다.

## 연습 문제

1. 렌즈 왜곡 항을 추가하고 영상 모서리에서 역투영한 점이 얼마나 움직이는지 보세요.
2. depth를 5x5 창의 median에서 읽고 그래도 실패하는 가장자리 픽셀을 찾으세요.
3. `fx = 600`이고 거리 2 m인 목표의 오차 예산을 mm로 계산하세요.
