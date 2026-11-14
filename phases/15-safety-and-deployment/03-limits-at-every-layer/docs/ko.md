# 계층별 한계 (Limits at Every Layer)

> 두 계층이 한계에 동의하지 않으면 더 빡빡한 쪽이 이기고 아무도 그것을 알리지 않습니다.

**유형:** 만들기   **선수 지식:** 15/02 Watchdog과 정지   **시간:** 약 15분

## 쉽게 말하면

작업대 위 로봇 팔은 명령을 세 계층을 거쳐 받아요. planner는 경로를 그리고 controller는 모터를 밀고 drive는 모터에 붙은 전자장치예요. 계층마다 자기 속도 한계가 있어요.

planner가 drive의 두 배 속도까지 허용한다고 해 보세요. planner는 팔이 자기 속도로 움직인다고 생각하지만 실제 팔은 drive의 속도로 움직여요. 그래서 계획이 앞서가고 간격이 벌어져요.
drive가 속도를 조용히 깎을 뿐이라 아무도 알려 주지 않아요. 가장 느린 한계가 이겨요.

## 문제

planner의 속도 한계를 3 rad/s로 올렸는데 관절은 그 절반으로 기어갑니다. drive가 자기 한계에 맞춰 속도를 조용히 clamp(잘라 냄)했기 때문에 에러는 남지 않았습니다. 위치와 속도와 토크는 세 계층에 각각 한계가 있고 세 세트가 맞는지 확인하는 곳은 없습니다.

## 개념

![정상 구조는 계층마다 앞 계층보다 느슨합니다](../assets/diagram-limits-nested.png)

*속도 한계가 1.0, 1.5, 2.0으로 커집니다. 계층마다 앞 계층보다 많이 허용하므로 뒤쪽 계층은 정상 상황에서는 작동하지 않는 안전망입니다.*

규칙은 이렇습니다. 각 양에 대해 planner에서 drive까지 따라갑니다. 모든 한계는 같은 양을 정하는 다음 계층보다 느슨하지 않아야 합니다. 곧 더 많이 허용하면 안 됩니다. 어기면 뒤쪽 계층이 이깁니다.

![어긋남이 있으면 가장 빡빡한 계층이 이기고 아무도 말하지 않습니다](../assets/diagram-limits-silent.png)

*요청이 계층을 따라 내려가는 것을 보세요. planner는 3.0을 요청하고 controller도 동의하지만 drive는 1.5만 허용합니다. 시작 점검은 모든 쌍을 비교해 첫 움직임 전에 보고합니다.*

계산 예입니다. 위치 한계가 planner 2.2와 controller 1.8과 drive 2.0일 때 2.0 rad를 요청합니다. 이것이 `MISMATCHED` 값입니다. planner와 drive는 이를 허용하지만 controller가 목표를 1.8로 잘라서 관절은 1.80 rad에서 멈춥니다.

`effective(MISMATCHED, "pos")`는 `(1.8, 'controller')`를 돌려줍니다.

![한 계층의 위치 한계가 낮아서 작업대 위 로봇 팔이 목표 앞에서 멈춥니다](../assets/clip-example.mp4)

*어두운 반투명 팔은 planner가 관절이 있다고 믿는 위치이고 주황색 블록은 목표입니다. 파란 팔은 경고 없이 0.2 rad 모자라게 멈춥니다. 초록은 위치 한계 세 개가 모두 2.0을 허용합니다.*

![두 구성의 계층별 한계](../assets/fig-limit-stack.png)

*파란색은 계층마다 올라가고 주황색은 속도와 토크와 위치에서 그 패턴을 깹니다.*

![두 구성의 기준 궤적과 관절 궤적](../assets/fig-limit-lag.png)

*목표와 게인은 같습니다. 한계가 맞으면 관절은 0.12 rad 뒤처집니다. 한계가 어긋나면 planner는 0.47초에 끝나는데 관절은 0.82 rad나 뒤에 있습니다.*

## 만들기

각 계층은 작은 dict이고 `None`은 그 계층이 한계를 정하지 않는다는 뜻입니다. 점검은 `None`을 건너뛰고 이웃끼리 비교합니다.

```python
for (a, x), (b, y) in zip(set_, set_[1:]):
    if x > y:
        out.append((q, a, b, x, y, f"{a}.{q} = {x} is looser than {b}.{q} = {y}: {b} wins silently"))
```

`require_nested()`는 모든 메시지를 담아 한 번만 예외를 냅니다. `effective()`는 관절이 실제로 느끼는 한계와 그 한계를 가진 계층을 돌려줍니다. `simulate()`는 PD loop 둘레에 clamp 세 개를 돌립니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/03-limits-at-every-layer -q
python3 phases/15-safety-and-deployment/03-limits-at-every-layer/code/main.py
```

## 실제 도구로 보기

실제 시스템은 한계를 URDF와 controller 설정과 drive 자체 parameter에 나눠 둡니다. 시작할 때 셋을 한 표로 읽어 같은 쌍 비교를 돌립니다. drive 한계는 사본이 아니라 drive에서 읽습니다.

## 결과물

`outputs/skill-limit-stack-audit.md`는 그 표를 만들고 보고를 읽는 체크리스트입니다.

## 연습 문제

1. planner의 토크 한계를 명시하고 점검을 거기까지 확장하세요.
2. 모든 계층에 가속도 한계를 추가하고 유효 한계를 보고하세요.
3. 점검이 같은 한계를 허용하는 이유와 여유를 두고 싶은 경우를 설명하세요.
