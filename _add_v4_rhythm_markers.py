import bpy

markers = [
    (0, "A01 势垒建立"),
    (90, "A02 势垒尺寸展示"),
    (300, "A03 势垒构图停稳"),
    (510, "A04 切到粒子15度镜头"),
    (600, "A05 跟随粒子向+X"),
    (720, "A06 抬升转向俯视"),
    (900, "A07 完成正上方构图"),
    (1050, "A08 粒子分解实部虚部"),
    (1121, "A09 平面分量展示"),
    (1180, "A10 拟合三维复波函数"),
    (1320, "A11 镜头沿Y轴移动"),
    (1560, "A12 概率密度浮现"),
    (1661, "A13 完整波系统传播"),
    (1740, "A14 公式与高亮"),
    (2040, "A15 概率图表同步"),
    (2880, "A16 宽度减至1_2W"),
    (3001, "A17 宽度扩至3_2W"),
    (3240, "A18 宽度恢复W"),
    (3420, "A19 高度降至0_8V0"),
    (3541, "A20 高度升至1_3V0"),
    (3780, "A21 高度恢复V0"),
    (3960, "A22 比较停留与叠加退出"),
    (4140, "A23 拉近透射波包"),
    (4380, "A24 坍缩回粒子"),
    (4500, "A25 结果与系综展开"),
    (4860, "A26 多粒子试验"),
]

scene = bpy.context.scene
for marker in list(scene.timeline_markers):
    if marker.name.startswith("A") and len(marker.name) >= 3 and marker.name[1:3].isdigit():
        scene.timeline_markers.remove(marker)

for frame, name in markers:
    scene.timeline_markers.new(name, frame=frame)

out = r"C:\Users\liuzh\Desktop\1\quantum_tunneling_scientific_v4_rhythm_marked.blend"
bpy.ops.wm.save_as_mainfile(filepath=out, check_existing=False)
print("WROTE", out, "MARKERS", len(markers))
