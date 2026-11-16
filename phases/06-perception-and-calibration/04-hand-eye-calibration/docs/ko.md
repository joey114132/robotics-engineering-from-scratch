# 손-눈 보정 (Hand-Eye Calibration)

> 로봇 손에 달린 카메라의 위치를 찾는 법과 팔이 서로 다른 축으로 돌아야 하는 이유를 배웁니다.

**유형:** 만들기   **선수 지식:** 01/04 Frame과 Transform 트리, 06/01 핀홀 카메라   **시간:** 약 15분

## 쉽게 말하면

카메라가 로봇 팔의 손에 고정되어 있어요. 팔은 카메라가 손의 어디에 있는지 알아야 하고 그것을 X라고 불러요.

팔을 움직여서 손이 움직인 모습과 카메라가 본 모습을 비교해요. 모든 움직임이 한 축으로만 돌면 카메라를 그 축을 따라 밀어도 달라지는 것이 없으니 여러 축으로 움직여요.

## 핵심 용어

- **Hand-eye calibration**: 카메라가 붙어 있는 gripper에 대해 카메라가 어디에 있는지 찾는 일입니다.
- **Transform (`X`)**: 한 frame을 다른 frame으로 옮기는 회전과 이동입니다. 여기서는 카메라에서 gripper로입니다.
- **Rotation axis**: 회전이 도는 중심선입니다.
- **SVD**: matrix 도구입니다. 여기서는 두 축 묶음을 맞추는 데 씁니다.
- **Singular value**: SVD가 내놓는 숫자입니다. 0에 가까우면 빠진 방향이 있다는 신호입니다.
- **Spread**: 움직임의 축들이 채우는 원뿔의 반각입니다.

## 문제

로봇 손의 카메라가 0.4 m 앞의 컵을 보는데 gripper가 컵을 놓칩니다. 카메라의 장착 위치 `X`를 모르고 한 축의 움직임은 그것을 가립니다.

## 개념

`X`가 없으면 카메라가 본 것을 손이 닿을 곳으로 바꿀 수 없습니다.

![식이 AX = XB인 이유](../assets/diagram-handeye-setup.png)

*움직임마다 두 번 잽니다. `A`는 관절에서, `B`는 카메라에서 나옵니다. `X`는 변하지 않습니다.*

움직임 하나는 회전 `R`과 이동 `t`입니다. 회전은 `R_A R_X = R_X R_B`이므로 `log(R_A) = R_X log(R_B)`입니다(`log(R)`은 축 곱하기 각도). SVD가 `R_X`를 줍니다.
이동은 `(R_A - I) t_X = R_X t_B - t_A`이고 `t_X`에 대해 선형입니다.

spread가 0이면 모든 축이 `z`이므로 `R_A z = z`이고 `R_A - I`가 `z`를 0으로 보내서 `t_X`를 `z`를 따라 옮겨도 어떤 식도 깨지지 않습니다.
노이즈가 있을 때 움직임 12개는 spread 0에서 121 mm와 136도의 오차를 주고 15에서 4.9 mm와 1.3도를 줍니다.

![팔이 도는 모습과 카메라 두 대](../assets/clip-example.mp4)

*팔이 세운 축을 중심으로 돕니다. 0.1 m 높은 카메라(유령)도 같은 움직임을 봅니다.*

![먼저 회전, 그다음 이동](../assets/diagram-handeye-solve.png)

*빨강: 축이 모두 평행하면 그 축을 중심으로 한 회전과 그 축을 따른 이동이 풀리지 않고 남습니다.*

![축 spread에 따른 오차](../assets/fig-handeye-spread.png)

*60번 노이즈 실행의 median입니다. 왼쪽은 한 축이 쓸모없다는 것입니다. 오른쪽은 축들의 둘째 대 첫째 singular value 비율(평행하면 0에 가까움)이 로봇이 움직이기 전에 경고하는 모습입니다.*

## 만들기

```python
U, s, Vt = np.linalg.svd(alpha.T @ beta)       # alpha = log(R_A), beta = log(R_B)
R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
t = np.linalg.lstsq(M, y, rcond=None)[0]       # M stacks (R_A - I), y stacks R_X t_B - t_A
```

`make_motions()`는 `A`를 만들고 `B = X^-1 A X`에 노이즈를 더합니다. `solve_hand_eye()`는 singular value도 돌려줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/04-hand-eye-calibration -q
```

## 실제 도구로 보기

OpenCV의 `cv2.calibrateHandEye`는 다섯 가지 방법을 제공하고 3개보다 훨씬 많은 pose를 권합니다.

출처: [OpenCV calibration module](https://docs.opencv.org/5.0/main_modules/calib.html)과 [OpenCV 3.4.20 calib3d reference](https://docs.opencv.org/3.4.20/d9/d0c/group__calib3d.html), 2026년 11월 9일 검색으로 찾았고 가져오기는 HTTP 403이었습니다.

## 결과물

`outputs/skill-hand-eye-check.md`는 로봇이 실행하기 전에 움직임의 축 다양성을 점검합니다.

## 연습 문제

1. translation에만 노이즈를 더하세요.
2. SVD 단계를 회전의 평균으로 바꿔 보세요.
3. spread 60도에서 움직임 개수에 따른 오차를 그리세요.
