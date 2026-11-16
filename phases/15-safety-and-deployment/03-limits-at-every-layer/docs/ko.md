# 계층별 한계 (Limits at Every Layer)

> 로봇이 부탁한 것보다 조용히 느리게 움직이는 이유와 시작할 때 잡아내는 법을 배웁니다.

**유형:** 만들기   **선수 지식:** 15/02 Watchdog과 정지   **시간:** 약 15분

## 쉽게 말하면

작업대 위 로봇 팔은 명령을 세 계층을 거쳐 받아요. planner는 경로를 그리고 controller는 모터를 밀고 drive는 모터에 붙은 전자장치예요. 계층마다 속도 한계가 있어요.

planner가 drive의 두 배 속도까지 허용하면 계획이 실제 팔보다 앞서가고 간격이 벌어져요. drive가 속도를 조용히 깎을 뿐이라 아무도 알려 주지 않아요. 가장 느린 한계가 이겨요.

## 핵심 용어

- **Planner**: 경로를 그리고 요청할 속도를 정하는 계층입니다.
- **Controller**: 경로를 모터 명령으로 바꾸는 계층입니다.
- **Drive**: 모터에 붙은 전자장치이고 자기 hard limit을 지킵니다.
- **Clamp**: 값이 한계 안에 머물도록 잘라 내는 것입니다.
- **Effective limit**: 가장 빡빡한 계층이 정해서 관절이 실제로 느끼는 한계입니다.
- **Nested limits**: 계층마다 다음 계층보다 많이 허용하지 않는 구조입니다.

## 문제

계획 소프트웨어의 속도 한계를 3 rad/s로 올렸는데 팔은 여전히 그 절반으로 기어가고 에러도 남지 않습니다. 모터 자체 전자장치의 더 낮은 한계가 속도를 조용히 깎았습니다.

## 개념

로봇에는 한계를 정하는 계층이 여럿이어서 어긋남은 문제가 생길 때까지 숨어 있습니다.

![nested 한계](../assets/diagram-limits-nested.png)

*속도 한계가 1.0, 1.5, 2.0으로 커집니다. 뒤쪽 계층은 정상 상황에서는 작동하지 않는 안전망입니다.*

규칙은 이렇습니다. 각 양에 대해 planner에서 drive까지 따라갑니다. 한계는 다음 계층의 한계보다 많이 허용하면 안 됩니다. 어기면 뒤쪽 계층이 이깁니다.

![조용한 어긋남](../assets/diagram-limits-silent.png)

*planner는 3.0을 요청하고 controller도 동의하지만 drive는 1.5만 허용합니다. 시작 점검은 모든 쌍을 비교해 첫 움직임 전에 보고합니다.*

예를 들어 위치 한계가 planner 2.2와 controller 1.8과 drive 2.0일 때(`MISMATCHED` 값) 2.0 rad를 요청합니다. controller가 목표를 1.8로 잘라서 관절은 1.80 rad에서 멈춥니다.
`effective(MISMATCHED, "pos")`는 `(1.8, 'controller')`를 돌려줍니다.

![목표 앞에서 멈춘 팔](../assets/clip-example.mp4)

*어두운 반투명 팔은 planner가 관절이 있다고 믿는 위치입니다. 파란 팔은 경고 없이 0.2 rad 모자라게 멈춥니다. 초록은 한계 세 개가 모두 2.0을 허용합니다.*

![한계 구성](../assets/fig-limit-stack.png)

*파란색은 계층마다 올라가고 주황색은 그 패턴을 깹니다.*

![한계와 지연](../assets/fig-limit-lag.png)

*한계가 맞으면 관절은 0.12 rad 뒤처집니다. 어긋나면 planner는 0.47초에 끝나는데 관절은 0.82 rad나 뒤에 있습니다.*

## 만들기

각 계층은 작은 dict이고 `None`은 한계가 없다는 뜻입니다. 점검은 `None`을 건너뛰고 이웃끼리 비교합니다.

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

실제 시스템은 한계를 URDF와 controller 설정과 drive 자체 parameter에 나눠 둡니다. 시작할 때 셋을 한 표로 읽어 같은 비교를 돌립니다.

## 결과물

`outputs/skill-limit-stack-audit.md`는 그 표를 만들고 보고를 읽습니다.

## 연습 문제

1. planner의 토크 한계를 명시하고 점검을 거기까지 확장하세요.
2. 모든 계층에 가속도 한계를 추가하세요.
3. 점검은 왜 같은 한계를 허용하나요?
