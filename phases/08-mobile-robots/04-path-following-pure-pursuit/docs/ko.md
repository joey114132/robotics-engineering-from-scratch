# Pure Pursuit로 경로 따라가기 (Path Following with Pure Pursuit)

> 경로 위에서 일정 거리 앞의 점을 겨냥하면 그 거리 하나가 흔들림과 코너 절단을 맞바꿉니다.

**유형:** 만들기   **선수 지식:** 08/01 차동 구동과 Odometry   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차가 바닥에 그린 선을 따라가면서 선 위의 앞쪽 한 점을 향해 핸들을 돌려요. 이 방식이 pure pursuit이고 그 앞쪽 거리가 lookahead예요.
점이 가까우면 옆으로 조금만 벗어나도 차가 크게 휙 돌아요. 바퀴가 늦게 반응해서 선을 넘어가면 다시 반대쪽으로 휙 돌아요.

점이 멀면 방향을 부드럽게 고쳐요. 하지만 굽은 길 근처에서는 점이 모퉁이 너머에 있어서 차가 코너를 가로질러요.

## 문제

모바일 로봇에 직각 코너가 있는 경로를 줍니다. lookahead가 짧으면 직선에서 뱀처럼 흔들리고 길면 코너를 가로질러 거기 서 있는 것에 부딪힙니다.

## 개념

![Pure pursuit 한 step](../assets/diagram-pp-step.png)

*경로에서 `Ld` 앞의 점을 고르고 옆으로 얼마나 떨어졌는지 재서 그 점에 닿는 원을 따라 조향합니다.*

로봇 좌표계(x는 앞, y는 왼쪽)에서 목표점은 `d`만큼 떨어져 있고 왼쪽으로 `y`만큼 벗어나 있습니다(음수면 오른쪽). 진행 방향으로 출발해 그 점을 지나는 원의 곡률은 `k = 2 y / d^2`입니다. 반지름이 `R`이면 `d^2 = 2 y R`이기 때문입니다.
곡률은 `1 / R`이므로 `|k|`가 클수록 급하게 도는 것입니다. 회전율은 앞으로 가는 속도 `v`에 대해 `w = v k`입니다. 회전율은 `w`에 서서히 다가가며 0.4초마다 차이의 3분의 2쯤을 줄입니다. 이 값은 측정값이 아니라 우리가 가정한 값입니다.

경로 왼쪽 0.6 m에서 경로를 따라 향한 채 출발하므로 `y = -0.6`입니다. `Ld = 0.4 m`이면 그만큼 가까운 경로 점이 없어서 가장 가까운 점이 목표점입니다. `d = 0.6`이고 `k = 2 * -0.6 / 0.6^2 = -3.3`이며 반지름 0.3 m인 원입니다.
`Ld = 1.5 m`이면 `d = 1.5`이고 `k = 2 * -0.6 / 1.5^2 = -0.53`이며 반지름은 1.9 m입니다.

![급한 첫 조향 원과 완만한 첫 조향 원](../assets/clip-example.mp4)

*얇은 호는 처음 조향하는 원입니다. 파란 차(`Ld = 0.4`)는 1.0초 뒤에 선을 넘고 초록 차(`Ld = 1.5`)는 2.8초 뒤에 넘습니다.*

![손잡이 하나, 실패 둘](../assets/diagram-pp-tradeoff.png)

*짧은 `Ld`는 가까운 점을 향해 세게 조향합니다. 긴 `Ld`는 코너 근처에서 경로에서 멀리 떨어진 점을 겨냥합니다.*

![같은 경로에서 lookahead 세 가지](../assets/fig-lookahead-paths.png)

*같은 출발입니다. 코너까지의 거리가 코너를 자른 정도입니다. `Ld = 0.4 m`는 선을 10번 가로지르지만 코너에 0.17 m까지 붙어 지나갑니다. 1.5 m는 안정되어 코너를 0.41 m 비켜 가고 4 m는 1.37 m 비켜 갑니다.*

지연이 없으면 짧은 lookahead도 흔들리지 않습니다. 테스트가 이를 보이므로 흔들림은 강한 보정(높은 gain)이 느린 구동부를 만난 결과입니다.

## 만들기

```python
def curvature(pose, target):
    dx, dy = target - pose[:2]
    y = -np.sin(pose[2]) * dx + np.cos(pose[2]) * dy
    return 2 * y / (dx * dx + dy * dy)

def lookahead_point(path, pos, ld):
    i = np.linalg.norm(path - pos, axis=1).argmin()
    far = np.nonzero(np.linalg.norm(path[i:] - pos, axis=1) >= ld)[0]
    return path[i + far[0]] if len(far) else path[-1]
```

`follow()`는 루프를 돌려 궤적을 돌려주고 `sign_changes()`는 선을 가로지른 횟수를 셉니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/04-path-following-pure-pursuit -q
python3 phases/08-mobile-robots/04-path-following-pure-pursuit/code/main.py
```

## 실제 도구로 보기

Nav2의 regulated pure pursuit controller는 앞쪽 경로 위의 점을 향해 조향합니다.

README는 알맞은 lookahead가 로봇 크기와 반응성, 갱신 주기, 속도에 달려 있다고 말하며 속도에 비례하는 lookahead도 제공합니다.

출처: Nav2 `nav2_regulated_pure_pursuit_controller` README, github.com/ros-navigation/navigation2, 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-pure-pursuit-tuning.md`는 흔들림 횟수와 코너 절단으로 `Ld`를 조정합니다.

## 연습 문제

1. `Ld`를 속도에 비례시키고 0.5 m/s와 2 m/s의 흔들림을 비교하세요.
2. 경로의 코너를 짧은 호로 둥글게 만들고 절단을 다시 재세요.
3. 지연 0.2초에서 선 가로지름이 2번 이하인 가장 작은 `Ld`를 찾으세요.
