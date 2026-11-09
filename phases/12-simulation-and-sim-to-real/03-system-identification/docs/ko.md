# System Identification

> 기록에서 plant를 맞추되 어떤 파라미터를 배울 수 있는지는 기록이 정한다는 것을 알아야 합니다.

**유형:** 만들기   **선수 지식:** 12/01 시뮬레이터가 근사하는 것   **시간:** 약 15분

## 문제

CAD에서 관성을 가져오고 마찰값은 짐작해서 넣은 뒤 궤적 하나가 맞을 때까지 시뮬레이터를 눈으로 튜닝합니다. 다음 궤적은 빗나갑니다. 그 궤적 하나로는 마찰과 감쇠를 구분할 수 없었기 때문입니다. 맞춘 결과는 좋아 보였지만 파라미터는 틀렸습니다.

## 개념

![기록된 한 번의 실행에서 파라미터까지](../assets/diagram-id-pipeline.png)

*짧은 구간마다 동역학을 적분하면 잡음 섞인 속도 샘플이 `J`, `b`, `c`에 대한 선형 문제가 됩니다. 모터 지연 `Tm`은 열 자체를 바꾸므로 격자 탐색이 풀이를 감쌉니다.*

한 구간에서 속도 변화는 `dw = (1/J) * int(tm - k sin q) - (b/J) * int(w) - (c/J) * int(tanh(w/eps))`입니다. 미지수 `1/J`, `b/J`, `c/J`가 선형으로 들어갑니다.

![느린 실행 하나가 b와 c를 못 가르는 이유](../assets/diagram-collinear.png)

*속도가 일정하면 점성 열과 쿨롱 열이 둘 다 상수이므로 최소제곱은 둘의 합만 볼 수 있습니다.*

![맞춘 결과, 느린 실행의 실패, 가진 크기에 따른 오차](../assets/fig-id-fit.png)

*왼쪽은 풍부한 실행의 데이터를 모델이 따라가는 모습입니다. 가운데는 느린 등속 실행 하나가 `b`를 참값의 -17배로 돌려주는 모습입니다. 오른쪽은 잡음을 고정하고 가진 크기를 키운 결과입니다. `J`는 0.1% 아래, `c`는 약 2%까지 내려가고 `b`는 8% 근처에 남습니다.*

## 만들기

`Tm` 후보마다 기록된 명령을 filter하고 세 열을 만든 다음 최소제곱을 풉니다. 잔차가 가장 낮은 후보가 이깁니다.

```python
for Tm in grid:
    X, y = design(d, Tm)
    th = np.linalg.lstsq(X, y, rcond=None)[0]
    fits.append((float(np.sum((y - X @ th) ** 2)), Tm, th, np.linalg.cond(X / np.linalg.norm(X, axis=0))))
```

잡음이 없을 때 열을 정규화한 condition number는 풍부한 실행에서 약 4, 느린 실행에서 약 2400입니다.

테스트는 `b = 0.02`를 `b = 0`으로 바꾸고 `c`에 `0.02 * 0.28`을 더합니다. 느린 실행은 거의 변하지 않고 풍부한 실행은 두 plant를 구분합니다. `b`에는 구간 적분 때문에 약 8%의 bias가 남습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/03-system-identification -q
python3 phases/12-simulation-and-sim-to-real/03-system-identification/code/main.py
```

## 실제 도구로 보기

`scipy.optimize.least_squares(fun, x0, bounds=...)`는 네 파라미터를 한꺼번에 맞추고 bound도 받습니다. 그 답과 공분산을 격자 fit과 비교해 보세요.

출처는 로컬 SciPy 1.11.4의 시그니처와 docstring입니다(2026년 11월 9일 확인).

## 결과물

`outputs/skill-excitation-check.md`는 fit하기 전에 기록이 충분한지 점검합니다.

## 연습 문제

1. J가 20% 틀어질 때까지 잡음을 키우고 어떤 구간 길이가 도움이 되는지 적으세요.
2. 알려진 중력 `k`를 네 번째 미지수로 넣고 condition number를 확인하세요.
3. `b`와 `c`를 가르는 가장 짧은 궤적을 설계하세요.
