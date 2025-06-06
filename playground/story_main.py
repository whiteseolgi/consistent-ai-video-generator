from scene2cut.scene_generator import SceneGenerator
from scene2cut.cut_generator import CutGenerator

# 예시 스토리
synopsis = "한 숲속에 평화롭게 살던 작은 생명이 있다. 어느 날 거대한 유성이 떨어지며 숲에 변화가 시작된다..."

scene_gen = SceneGenerator()
scenes = scene_gen.generate_scenes(synopsis)

print("scenes output")
for s in scenes:
    print(s)

cut_gen = CutGenerator()
cuts = cut_gen.cut_scene(scenes[0])

print("first cut outputs: ")
for c in cuts:
    print(c)