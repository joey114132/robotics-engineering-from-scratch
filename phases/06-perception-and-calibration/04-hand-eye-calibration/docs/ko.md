# 손-눈 보정 (Hand-Eye Calibration)

> gripper에 고정한 카메라는 모든 움직임을 두 번 봅니다. `A X = X B`로 카메라 위치를 찾지만 로봇이 한 축만이 아니라 여러 축으로 회전해야 풀립니다.

**유형:** 만들기   **선수 지식:** 01/04 Frame과 Transform 트리, 06/01 핀홀 카메라   **시간:** 약 15분

## 쉽게 말하면

카메라가 로봇 팔의 손에 고정되어 있고 팔은 카메라에 보이는 컵을 집어야 해요. 카메라는 컵을 자기 시야 안의 위치로 알려 주기 때문에 팔은 카메라가 손의 어디에 달려 있는지를 알아야 해요. 그 관계를 X라고 불러요.

X를 구하려면 팔을 움직이면서 손이 움직인 모양과 카메라가 본 모양을 비교해요. 매번 한 축으로만 돌면 그 축을 따라 카메라를 옮겨도 같은 움직임이 나오기 때문에 그 축 방향의 위치는 알 수 없어요. 다른 축으로 돌리면 이 문제가 풀려요.

## 문제

카메라는 컵이 0.4 m 앞에 있다고 보고 gripper는 그곳으로 가야 합니다. 카메라에서 gripper로 가는 변환 `X`를 모르면 gripper는 그 미지의 오프셋만큼 틀린 곳으로 갑니다.
매번 한 축으로만 도는 동작으로 보정하면 결과가 멀쩡해 보이지만 틀립니다.

## 개념

![왜 AX = XB인가](../assets/diagram-handeye-setup.png)

*움직임 하나를 두 번 잽니다. 관절로 `A`를 재고 카메라로 `B`를 잽니다. `X`는 변하지 않으므로 `A X = X B`가 성립합니다.*

움직임 하나는 회전 `R`과 이동 `t`입니다. `A X = X B`를 곱해서 풀면 두 부분이 나옵니다.
회전 부분은 `R_A R_X = R_X R_B`이므로 `R_A`는 `R_X`를 거쳐 본 `R_B`입니다. 각도는 같고 축만 `R_X`만큼 돌아가므로 `log(R_A) = R_X log(R_B)`입니다(`log(R)`은 축에 각도를 곱한 벡터입니다). SVD로 두 축 묶음을 맞춰 `R_X`를 구합니다.
이동 부분은 `R_A t_X + t_A = R_X t_B + t_X`이므로 `(R_A - I) t_X = R_X t_B - t_A`이고 `t_X`에 대해 선형입니다.

예를 들어 움직임들의 회전축이 `z` 주위의 원뿔 안에 있다고 하고 그 반각을 spread라고 부릅니다. spread 0이면 모든 축이 `z`이므로 `R_A z = z`이고 `R_A - I`는 `z`를 0으로 보냅니다. 그래서 `t_X`를 `z` 방향으로 옮겨도 어떤 식도 깨지지 않습니다.
잡음이 있을 때 움직임 12개의 오차는 spread 0에서 121 mm와 136도이고 spread 15에서 4.9 mm와 1.3도입니다.

![카메라 두 대 중 하나가 0.1 m 높은 채 도는 팔](../assets/clip-example.mp4)

*팔은 수직축 하나로 돕니다. 그 축 위로 0.1 m 높은 카메라(반투명)도 같은 원을 그리므로 이 움직임만으로는 둘을 구별하지 못합니다.*

![회전 먼저, 이동 나중](../assets/diagram-handeye-solve.png)

*빨간 상자는 실패 경우입니다. 축이 모두 평행하면 그 축 주위의 회전과 그 축 방향 이동이 정해지지 않습니다.*

![회전축 퍼짐에 따른 오차](../assets/fig-handeye-spread.png)

*잡음이 있는 60회 실행의 median입니다. 왼쪽은 한 축이면 답이 쓸모없고 몇 도만 퍼져도 나아지는 모습입니다. 오른쪽은 축의 둘째/첫째 singular value 비율(거의 같은 방향이면 0에 가깝습니다)로 계획한 움직임만으로 알 수 있어 움직이기 전에 경고합니다.*

## 만들기

```python
U, s, Vt = np.linalg.svd(alpha.T @ beta)       # alpha = log(R_A), beta = log(R_B)
R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
t = np.linalg.lstsq(M, y, rcond=None)[0]       # M stacks (R_A - I), y stacks R_X t_B - t_A
```

`make_motions()`는 `A`를 만들고 `B = X^-1 A X`에 잡음을 더합니다. `solve_hand_eye()`는 singular value `s`도 함께 돌려줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/04-hand-eye-calibration -q
```

## 실제 도구로 보기

OpenCV에는 `cv2.calibrateHandEye(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, method=...)`가 있습니다.
다섯 가지 방법을 지원하고 자세를 3개보다 훨씬 많이 쓰라고 권장합니다.
테스트는 이 함수가 돌려준 회전을 정답 `X`와 비교합니다.

출처는 [OpenCV calibration 모듈](https://docs.opencv.org/5.0/main_modules/calib.html)과
[OpenCV 3.4.20 calib3d 레퍼런스](https://docs.opencv.org/3.4.20/d9/d0c/group__calib3d.html)입니다.
내용은 2026년 11월 9일 검색 결과에서 가져왔고 페이지 자체는 자동 fetch에서 HTTP 403을 돌려주었습니다.

## 결과물

`outputs/skill-hand-eye-check.md`는 로봇으로 돌리기 전에 보정 움직임의 축 다양성을 확인합니다.

## 연습 문제

1. 이동에만 잡음을 넣고 `X`의 어느 부분이 나빠지는지 보세요.
2. SVD 단계를 축 쌍 회전의 평균으로 바꾸고 비교하세요.
3. 축 퍼짐 60도에서 움직임 수에 따른 오차를 그리세요.
