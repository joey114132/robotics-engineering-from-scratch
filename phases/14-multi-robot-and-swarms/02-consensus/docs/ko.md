# 합의 (Consensus)

> 이웃과만 통신하는 로봇들도 숫자 하나에 합의할 수 있고 합의 속도는 그래프 Laplacian의 두 번째로 작은 고유값이 정합니다.

**유형:** 만들기   **선수 지식:** 대칭 행렬의 고유값   **시간:** 약 15분

## 문제

로봇 여덟 대가 같은 양을 각자 다른 오차로 재는데 나머지 전부의 소리를 듣는 로봇은 없습니다. 무전이 닿는 이웃과 메시지만 주고받아 모두가 그룹 평균을 갖게 하려고 합니다. 배치에 따라 열 번 남짓이면 되기도 하고 수백 번이 걸리기도 합니다. 갈라진 무리는 끝내 합의하지 못합니다.

## 개념

![합의 갱신 한 번](../assets/diagram-consensus-update.png)

*로봇은 tick마다 이웃의 평균 쪽으로 조금씩 움직입니다.*

![모드마다 줄어드는 속도가 다릅니다](../assets/diagram-consensus-modes.png)

*불일치는 여러 모드로 나뉩니다. 빠른 모드는 금방 사라지고 가장 느린 모드가 속도를 정합니다. 고유값이 0이면 그 모드는 줄지 않습니다.*

![세 그래프에서 상태가 수렴하는 모습](../assets/fig-consensus-states.png)

*링은 평균까지 느리게 기어갑니다. 완전 그래프는 열 step쯤에 도착하고 끊어진 두 무리는 서로 다른 값에 멈춥니다.*

![측정한 속도와 eps 곱하기 lambda2](../assets/fig-rate-vs-lambda2.png)

*크기가 다른 링, 완전, path, star 그래프가 모두 y = x 선 위에 놓입니다. 측정한 감쇠 속도가 eps 곱하기 lambda2입니다.*

`L = D - A`로 두면 갱신식은 `x <- (I - eps L) x`입니다. `L`은 대칭이고 행의 합이 0이라서, 모든 성분이 1인 벡터의 고유값이 0이고 평균은 변하지 않습니다. 나머지 고유벡터 `v_k`는 매 step `1 - eps * lambda_k`배가 됩니다.

`eps * lambda_max < 2`이면 안정합니다. `eps`가 충분히 작아서 어느 모드도 부호가 뒤집히지 않으면 가장 느린 감쇠는 `1 - eps * lambda2`입니다. 두 번째 고유값은 그래프가 연결되어 있을 때에만 0보다 큽니다.

## 만들기

`laplacian()`은 `D - A`를 만듭니다. `lambda2()`는 정렬한 두 번째 고유값을 꺼내고 `run()`은 갱신을 반복합니다.

```python
M = np.eye(len(A)) - eps * laplacian(A)
out.append(M @ out[-1])
```

테스트는 평균이 보존되는지, step당 수축 비율이 `1 - eps * lambda2`와 같은지, `2 / lambda_max`를 넘는 step이 발산하는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/14-multi-robot-and-swarms/02-consensus -q
python3 phases/14-multi-robot-and-swarms/02-consensus/code/figure.py
```

## 실제 도구로 보기

실제 무전 기록에서 만든 그래프로 `numpy.linalg.eigvalsh`와 `lambda2`를 대조해 보세요.

출처는 Wikipedia의 Algebraic connectivity 문서입니다(2026년 11월 9일 확인). "This eigenvalue is greater than 0 if and only if G is a connected graph."라고 적혀 있습니다.

## 결과물

`outputs/skill-consensus.md`는 로봇 무리가 합의를 돌리기 전에 통신 그래프와 step 크기를 점검합니다.

## 연습 문제

1. 링에 장거리 연결을 하나 더하고 `lambda2`와 step 수가 얼마나 변하는지 재세요.
2. tick마다 각 연결을 확률 0.2로 끊고 합의까지 걸리는 평균 step 수를 그리세요.
3. 로봇 0의 값을 고정하면 모두가 그 값으로 수렴함을 보이세요.
