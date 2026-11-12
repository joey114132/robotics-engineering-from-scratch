# Pose Graph와 루프 폐쇄 (Pose Graph and Loop Closure)

> pose를 미지수로 두고 측정을 그 사이의 스프링으로 보면 늦게 들어온 "여기로 돌아왔다"는 측정 하나가 표류한 궤적 전체를 닫아 줍니다.

**유형:** 만들기   **선수 지식:** 08/05 ICP 스캔 정합, 07/02 칼만 필터   **시간:** 약 15분

## 쉽게 말하면

학교를 돌아 걸은 길을 그렸는데 마지막 표시가 입구에서 떨어져 있어요. 실제로는 익숙한 입구에 돌아왔어요. 마지막 표시만 옮겨도 앞에서 그린 모퉁이들은 여전히 틀려요.

pose graph는 기록한 자리들을 측정한 이동으로 연결해요. 입구를 다시 알아보면 끝과 시작을 잇는 loop closure가 생겨요. 시작점은 고정하고 더 믿을 만한 측정에 더 맞추며 다른 pose를 함께 고쳐요. 다른 문을 입구로
착각하면 지도 전체가 잘못 끌려갈 수 있어요.

## 문제

5 m 정사각형을 돌았는데 오도메트리는 로봇이 출발점에서 1.4 m 떨어져 끝났다고 말합니다. 그때 스캔 정합(08/05)이 마지막 스캔이 첫 스캔과 똑같다고 알려 줍니다. 마지막 pose만 덮어쓰면 점 하나만 고쳐집니다.

이전의 모든 pose와 그것으로 만든 지도는 여전히 휘어 있습니다.

## 개념

![pose는 미지수이고 edge는 스프링입니다](../assets/diagram-posegraph-springs.png)

*오도메트리 한 걸음이 이웃한 pose 사이의 스프링입니다. 루프 폐쇄는 마지막 pose에서 첫 pose로 가는 스프링 하나를 더합니다.*

pose는 `(x, y, heading)`입니다. pose `i`에서 `j`로 가는 edge는 `i`에서 본 `j`의 pose인 측정 `z`를 가집니다. 잔차는 `between(x_i, x_j) - z`이고 heading 차이는 wrap합니다. 잔차를 각자의 노이즈로 나누어 믿을 만한 스프링일수록 뻣뻣하게 만듭니다. cost는 잔차 제곱의 합입니다.

![늦은 보정이 오래된 pose를 고치는 과정](../assets/diagram-posegraph-pipeline.png)

*폐쇄 edge 하나가 그래프에 들어오면 solver가 모든 pose를 한꺼번에 다시 풉니다.*

Gauss-Newton은 잔차를 선형화하고 최소제곱 한 걸음을 풀고 반복합니다. 모든 pose가 자유로우면 지도 전체를 옮기거나 돌려도 잔차가 변하지 않아서 세 방향이 정해지지 않습니다. pose 0을 고정하면 이것이 사라집니다.

![루프 폐쇄 전후의 궤적](../assets/fig-posegraph-loop.png)

*왼쪽은 오도메트리가 열린 채 표류하고 푼 궤적이 정사각형에 겹치는 모습입니다. 오른쪽은 오차가 끝에서만이 아니라 루프 전체에서 줄어드는 모습입니다.*

폐쇄 edge는 하나의 주장입니다. 틀린 주장은 없는 것보다 지도를 더 휘게 만들고 테스트가 이것을 확인합니다.

## 만들기

```python
def residuals(X, edges):
    out = []
    for i, j, z, w in edges:
        e = between(X[i], X[j]) - z
        e[2] = wrap(e[2])
        out.append(w * e)
    return np.concatenate(out)

J = jacobian(X, edges, free=range(1, len(X)))   # numeric, pose 0 held fixed
dx = np.linalg.lstsq(J, -residuals(X, edges), rcond=None)[0]
```

테스트는 cost가 오르지 않는지, pose 0이 움직이지 않는지, 고정 안 한 Jacobian의 rank가 `3n - 3`인지, 틀린 폐쇄가 더 나쁜 지도를 주는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/06-pose-graph-and-loop-closure -q
python3 phases/08-mobile-robots/06-pose-graph-and-loop-closure/code/main.py
```

## 실제 도구로 보기

g2o는 SLAM을 pose와 제약의 그래프로 보고 Gauss-Newton이나 Levenberg-Marquardt로 비선형 최소제곱을 풉니다. 같은 그래프를 그쪽에 만들어 `solve()`와 pose를 비교해 보세요.

출처는 Kümmerle 외, g2o: A General Framework for Graph Optimization (ICRA 2011)입니다(http://ais.informatik.uni-freiburg.de/publications/papers/kuemmerle11icra.pdf). 2026년 11월 10일 검색으로 찾았고 요약 수준만 읽었습니다.

## 결과물

`outputs/skill-pose-graph-check.md`는 pose graph 풀이의 빠진 anchor, 잘못된 edge 가중치, 거짓 폐쇄를 점검합니다.

## 연습 문제

1. heading bias를 없애고 폐쇄가 지도를 여전히 얼마나 움직이는지 보세요.
2. 루프 폐쇄의 확신을 10배 낮추고 오차가 퍼지는 모습을 보세요.
3. pose 5와 15 사이에 폐쇄를 하나 더 넣고 오차를 비교하세요.
