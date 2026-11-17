# 레슨 00/01 테스트: sense, think, act 한 바퀴와 되풀이 루프가 벽 앞에서 멈추는지, 센서 없는 자동차는 벽을 넘는지 확인한다
import importlib.util
import pathlib

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_robot", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_sense_is_the_gap_to_the_wall():
    assert m.sense(0.0, wall=3.0) == 3.0
    assert m.sense(2.5, wall=3.0) == 0.5


def test_think_goes_when_far_and_stops_when_close():
    assert m.think(2.0) == m.SPEED
    assert m.think(0.3) == 0.0


def test_act_moves_by_speed_times_step():
    assert abs(m.act(1.0, 2.0, dt=0.1) - 1.2) < 1e-12


def test_loop_stops_before_the_wall():
    run = m.drive(wall=3.0)
    assert max(run["position"]) < 3.0
    assert 0.4 - 1e-9 <= run["distance"][-1] <= 0.5 + 1e-9


def test_same_loop_works_for_a_wall_further_away():
    run = m.drive(wall=5.0, seconds=8.0)
    assert 0.4 - 1e-9 <= 5.0 - run["position"][-1] <= 0.5 + 1e-9


def test_blind_car_drives_through_the_wall():
    assert m.blind_drive(seconds=4.0) > 3.0


def test_loop_repeats_sense_think_act_every_step():
    run = m.drive(seconds=2.0, dt=0.1)
    assert len(run["position"]) == 21 and len(run["speed"]) == 21
