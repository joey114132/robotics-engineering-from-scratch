# 레슨 00/01 클립: sense-think-act 고리로 달리는 장난감 자동차(초록)가 벽 앞 0.5 m 에서 멈춘다. 호박색 막대는 센서가 읽은 거리
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS = 4.5
run = m.drive(seconds=SECONDS)                       # the lesson's own loop, one row per 0.1 s pass

sc = kit.setup(SECONDS)
kit.stripe(-0.8, 3.8, -0.7, 0.7, "road")
kit.box("wall", (0.12, 1.4, 0.5), (m.WALL + 0.06, 0, 0.25), "grey", bevel=0.01)
car, wheels, brake = kit.car("loop", "green")
beam = kit.arrow("sensor", "amber", shaft=0.012)      # a bar from the nose to the wall: what the distance sensor reads
beam.location = (0, 0, 0.13)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int(round((f - 1) / sc.render.fps / m.DT)), len(run["position"]) - 1)
    x = run["position"][i]                            # the nose is the measured point
    kit.drive(car, wheels, f, x - 0.3)
    kit.key(beam, f, loc=(x, 0, 0.13))
    beam.scale = (run["distance"][i], 1, 1)
    beam.keyframe_insert("scale", frame=f)
kit.camera((1.5, -3.9, 1.7), (1.5, 0, 0.2), lens=35)
kit.render(__file__)
