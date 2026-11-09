# 궤적 프로파일 (Trajectory Profiles)

> 두 점 사이의 경로를 고르는 것은 쉽습니다. 모터가 덜컥거리지 않고 따라가려면 조건이 네 개가 아니라 여섯 개 있어야 합니다.

**유형:** 만들기   **선수 지식:** 고등학교 미적분   **시간:** 약 15분

## 문제

관절이 한 자세에서 다른 자세로 부드러워 보이는 곡선을 따라 움직이는데도 출발할 때 덜컥 소리가 납니다. 곡선은 양 끝에서 속도가 0이고 목표 위치에 정확히 도착하므로 위치와 속도에는 문제가 없습니다. 원인은 가속도입니다. 제어 주기 한 번 사이에 가속도가 0에서 큰 값으로 뜁니다.

## 개념

![세 프로파일과 가속도에 미치는 영향](../assets/diagram-profile-choice.png)

*cubic, quintic, trapezoid는 모두 같은 이동을 합니다. 양 끝에서 가속도가 어떻게 움직이는지가 다릅니다.*

시간에 대한 다항식은 조건 하나에 계수 하나가 필요합니다. 양 끝의 위치와 속도가 네 조건이므로 cubic이 됩니다. 양 끝의 가속도까지 넣으면 여섯 조건이므로 quintic입니다.

`s = t/T`, `d = qf - q0`로 두면 quintic은 `q0 + d(10 s^3 - 15 s^4 + 6 s^5)`입니다.

![위치, 속도, 가속도를 나란히 그린 그림](../assets/fig-profiles.png)

*세 프로파일 모두 정지 상태로 목표에 도착합니다. 시작과 끝의 가속도가 0인 것은 quintic뿐입니다.*

![가속도 계단이 jerk가 되는 과정](../assets/diagram-jerk-chain.png)

*가속도의 계단은 jerk의 뾰족한 값이 되고 모터에는 토크의 계단으로 전달됩니다.*

![샘플 주기에 따른 최대 jerk](../assets/fig-jerk-vs-dt.png)

*샘플 주기를 절반으로 줄이면 cubic과 trapezoid의 jerk는 두 배가 됩니다. quintic은 `60 d / T^3`에 머뭅니다.*

## 만들기

```python
def quintic(q0, qf, T):
    d = qf - q0
    return np.array([q0, 0.0, 0.0, 10*d/T**3, -15*d/T**4, 6*d/T**5])
```

`poly`는 계수로 위치, 속도, 가속도를 계산합니다. `trapezoid`는 `ta` 동안 가속하고 `d/(T-ta)`로 순항한 뒤 감속합니다. `peak_jerk`는 이동 전후에 관절이 정지해 있다고 보고 계산하므로 계단이 바로 거기서 생깁니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/01-trajectory-profiles -q
python3 phases/09-motion-planning/01-trajectory-profiles/code/main.py
```

## 실제 도구로 보기

SciPy의 `BPoly.from_derivatives`는 양 끝의 미분값으로 같은 quintic을 만들고 마지막 테스트가 둘을 비교합니다.

출처: Craig, *Introduction to Robotics*, 3판, 7장 (궤적 생성).

## 결과물

`outputs/skill-trajectory-profile-check.md`는 프로파일이 관절에 닿기 전에 경계 조건과 jerk를 확인합니다.

## 연습 문제

1. 양 끝의 jerk 0을 일곱 번째 조건으로 더하고 필요한 차수를 말하세요.
2. trapezoid에서 최대 가속도를 주어진 한계 아래로 두는 가장 작은 `ta`를 구하세요.
3. 이동 시간을 `2T`로 두 배 늘린 quintic의 최대 가속도가 4분의 1이 되는 것을 보이세요.
