# System Identification

> 녹화에서 로봇 관절의 숨은 수치를 재는 법과 단조로운 녹화가 실패하는 이유를 배웁니다.

**유형:** 만들기   **선수 지식:** 12/01 시뮬레이터가 근사하는 것   **시간:** 약 15분

## 쉽게 말하면

매달린 팔을 일정한 속도로 돌려 보세요. 미는 힘의 일부는 일정한 마찰을 이기고 나머지는 속도가 클수록 커지는 저항을 이겨요. 속도가 하나뿐이면 마찰과 저항을 구분할 수 없어요.

이제 속도를 바꿔 보세요. 저항은 속도를 따라 변하고 마찰은 그렇지 않아서 둘이 갈라져요. 이런 기록에 모델을 맞추는 일을 system identification이라고 해요.

## 핵심 용어

- **Inertia (`J`)**: 팔의 속도를 올리기 어려운 정도입니다.
- **Drag (`b`)**: 속도가 클수록 커지는 저항입니다.
- **Rub (`c`)**: 움직임의 반대 방향으로 일정하게 작용하는 저항입니다.
- **Motor lag (`Tm`)**: 명령 뒤에 모터의 힘이 얼마나 늦게 오는지입니다.
- **Least squares**: 모델이 녹화에서 최대한 덜 벗어나도록 수치를 고르는 방법입니다.
- **Excitation**: 기록 속 움직임이 얼마나 다양한지입니다.

## 문제

설계 파일의 숫자와 마찰의 짐작으로 시뮬레이션 팔을 만들었더니 움직임 하나는 맞는데 실제 팔의 다음 움직임은 빗나갑니다.

## 개념

시뮬레이터를 믿으려면 실제 숫자가 필요하고 실제 팔의 녹화가 그 숫자를 줄 수 있습니다. 컴퓨터가 시뮬레이션 팔이 녹화와 맞아떨어지게 하는 숨은 수치를 찾습니다.
하지만 팔이 일정한 속도로만 움직였다면 마찰과 저항이 똑같아 보여서 컴퓨터가 둘을 나눌 수 없습니다. 속도가 올라갔다 내려가면 나눌 수 있습니다.

![파이프라인](../assets/diagram-id-pipeline.png)

*녹화를 넣으면 숨은 수치가 나옵니다.*

![Collinear](../assets/diagram-collinear.png)

*일정한 속도에서는 마찰과 저항이 둘 다 일정해서 둘의 합만 보입니다.*

![Fit](../assets/fig-id-fit.png)

*왼쪽은 모델이 다양한 녹화를 따라가는 모습입니다. 가운데는 느린 일정한 실행 하나가 저항을 크게 틀리게 내는 모습입니다. 오른쪽은 excitation(다양한 움직임)이 클수록 더 잘 맞는 모습입니다.*

![두 기록](../assets/clip-example.mp4)

*속도가 일정한 기록(파랑)은 틀린 저항을 내고 속도가 달라지는 기록(초록)은 맞는 저항을 냅니다.*

<details><summary>The math (optional)</summary>

저항 `b`는 viscous damping, 마찰 `c`는 Coulomb friction이라고도 부릅니다.
짧은 구간에서 모터 토크에서 중력과 저항과 마찰을 뺀 값을 더하면 `J`에 속도 변화를 곱한 값과 같아서 미지수는 `1/J`, `b/J`, `c/J`뿐입니다. 모터 지연 `Tm`은 격자로 훑습니다.
느린 실행은 0.28 rad/s에 머물고 저항 `b = 0.02`와 마찰 `c = 0.05`가 미는 힘은 합쳐서 0.0556입니다.
fit은 `b = -0.345`와 `c = 0.153`을 돌려주는데 이것도 합이 0.056이라서 데이터로는 고를 수 없고 `b`는 참값의 -17배가 됩니다.
다양한 실행에서는 속도가 3.35 rad/s까지 올라가고 fit이 `b = 0.0206`을 돌려줍니다. excitation을 키우면 `J`는 0.1% 아래, `c`는 약 2%까지 내려가지만 `b`는 8% 근처에 남습니다.
condition number(파라미터가 얼마나 뭉개지는지 나타내는 값)는 다양한 실행에서 약 4, 느린 실행에서 약 2400입니다.

</details>

## 만들기

모터 지연을 하나 짐작할 때마다 녹화된 명령을 모터가 실제로 할 동작으로 바꾸고 나머지 수치는 least squares로 찾습니다. 가장 잘 맞는 것이 이깁니다.

```python
for Tm in grid:
    X, y = design(d, Tm)
    th = np.linalg.lstsq(X, y, rcond=None)[0]
    fits.append((float(np.sum((y - X @ th) ** 2)), Tm, th, np.linalg.cond(X / np.linalg.norm(X, axis=0))))
```

다양한 녹화는 또렷한 결과를 주고 느리고 일정한 녹화는 흐릿한 결과를 줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/03-system-identification -q
python3 phases/12-simulation-and-sim-to-real/03-system-identification/code/main.py
```

## 실제 도구로 보기

SciPy의 `scipy.optimize.least_squares`는 네 수치를 한꺼번에 맞출 수 있습니다.

출처: SciPy 1.11.4의 시그니처와 docstring(2026년 11월 9일 확인).

## 결과물

`outputs/skill-excitation-check.md`는 fit하기 전에 기록이 충분한지 점검합니다.

## 연습 문제

1. 잡음을 더 키우세요. 관성은 언제 틀어지나요?
2. 중력도 미지수로 두고 수치를 하나 더 맞춰 보세요.
3. 속도가 충분히 변해서 마찰과 저항을 가르는 가장 짧은 녹화를 찾으세요.
