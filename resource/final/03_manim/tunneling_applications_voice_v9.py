"""Voice-aligned NB14/NB15 applications montage.

Global timeline F09709-F10795 inclusive (1087 frames at 60 fps).  The source
keeps the V8 stage/dock/final geometry, but every material action is retimed to
the narration cues supplied by the user.  Only the active centre-stage demo
moves; docked and background objects remain still under a spotlight scrim.
"""

from __future__ import annotations

import math
import numpy as np
from manim import *
from manim.utils.rate_functions import ease_in_out_cubic, ease_out_cubic, rush_into

from tunneling_applications_resolve_v8 import (
    BG, WHITE_C, CYAN, CYAN_LIGHT, ORANGE, RED, YELLOW, GREEN, GREY,
    STAGE_SHIFT,
    TUNNEL_DOCK, APP_DOCKS, INTERMEDIATE_APP_SCALES,
    FINAL_TUNNEL, FINAL_APPS, FINAL_APP_SCALE_FACTORS,
    make_tunnel_source, make_source_arrow, make_nand, make_stm, make_cmos, txt,
)


FPS = 60
GLOBAL_START = 9709
GLOBAL_END = 10795

config.background_color = BG
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = FPS


def spotlight_scrim() -> Rectangle:
    return Rectangle(
        width=config.frame_width,
        height=config.frame_height,
        fill_color=BG,
        fill_opacity=0.0,
        stroke_width=0,
    ).set_z_index(10)


class TunnellingApplicationsVoiceV9(Scene):
    def setup(self) -> None:
        self.cursor = 0

    def wait_to(self, global_frame: int) -> None:
        target = global_frame - GLOBAL_START
        frames = target - self.cursor
        if frames > 0:
            self.wait(frames / FPS)
            self.cursor = target

    def play_through(self, global_end: int, *animations: Animation, rate_func=ease_in_out_cubic) -> None:
        target = global_end - GLOBAL_START + 1
        frames = target - self.cursor
        if frames <= 0:
            raise ValueError(f"Non-positive exact-frame animation at F{global_end:05d}")
        self.play(*animations, run_time=frames / FPS, rate_func=rate_func)
        self.cursor = target

    def construct(self) -> None:
        self.camera.background_color = BG

        # Seamless first frame from NB12's final 2D tunnelling diagram.
        projection = make_tunnel_source().scale(0.86).move_to(LEFT * 0.68)
        self.add(projection)
        self.play_through(9772, projection.animate.scale(1.012), rate_func=there_and_back)
        self.play_through(9940, projection.animate.scale(0.645 / 1.012).move_to(TUNNEL_DOCK).set_opacity(0.30))

        # NAND becomes visible exactly at local 00:06:00 (global F10069) and
        # still finishes on the narration-locked F10273.
        scrim_n = spotlight_scrim()
        arrow_n = make_source_arrow(ORANGE).set_z_index(24)
        self.add(scrim_n)
        self.play_through(10068, scrim_n.animate.set_fill(opacity=0.76), Create(arrow_n[0]), FadeIn(arrow_n[1], scale=0.5))
        nand = make_nand()
        nand["all"].set_z_index(22)
        self.play_through(10098, FadeIn(nand["title"], shift=UP * 0.12), FadeIn(nand["cell"]), FadeIn(nand["data"]))
        self.play_through(10118, GrowArrow(nand["hv"][0]), FadeIn(nand["hv"][1]))

        x_positions = np.linspace(nand["oxide"].get_left()[0] + 0.30, nand["oxide"].get_right()[0] - 0.30, 9)
        electrons = VGroup(*[
            Dot([x, nand["oxide"].get_bottom()[1] - 0.36, 0], radius=0.075, color=CYAN_LIGHT)
            for x in x_positions
        ])
        self.add(electrons)
        self.play_through(
            10158,
            LaggedStart(*[dot.animate.move_to([dot.get_x(), nand["fg"].get_center()[1], 0]) for dot in electrons], lag_ratio=0.08),
            rate_func=rush_into,
        )
        erased_bits = VGroup(*[txt("11111111", 27, ORANGE, font="Courier New") for _ in range(4)]).arrange(DOWN, buff=0.18).move_to(nand["bits"])
        erased_state = txt("状态: 已擦除 (FF)", 22, ORANGE).move_to(nand["state"])
        erased_charge = txt("浮栅电荷: ○○○○○", 22, GREY).move_to(nand["charge"])
        self.play_through(10198, FadeOut(electrons), Transform(nand["bits"], erased_bits),
                          Transform(nand["state"], erased_state), Transform(nand["charge"], erased_charge))

        write_xs = np.linspace(nand["oxide"].get_left()[0] + 0.48, nand["oxide"].get_right()[0] - 0.48, 6)
        write_electrons = VGroup(*[
            Dot([x, nand["oxide"].get_bottom()[1] - 0.34, 0], radius=0.075, color=CYAN_LIGHT)
            for x in write_xs
        ])
        self.add(write_electrons)
        programmed_bits = VGroup(*[
            txt(value, 27, GREEN, font="Courier New")
            for value in ("00110111", "10101010", "01110001", "11001100")
        ]).arrange(DOWN, buff=0.18).move_to(nand["bits"])
        programmed_state = txt("状态: 写入数据", 22, GREEN).move_to(nand["state"])
        programmed_charge = txt("浮栅电荷: ●●○●○", 22, CYAN).move_to(nand["charge"])
        self.play_through(
            10238,
            LaggedStart(*[dot.animate.move_to([dot.get_x(), nand["fg"].get_center()[1], 0]) for dot in write_electrons], lag_ratio=0.10),
            Transform(nand["bits"], programmed_bits),
            Transform(nand["state"], programmed_state),
            Transform(nand["charge"], programmed_charge),
            rate_func=rush_into,
        )
        self.play_through(
            10273,
            FadeOut(VGroup(write_electrons, arrow_n)),
            nand["all"].animate.scale(INTERMEDIATE_APP_SCALES[0]).move_to(APP_DOCKS[0]).set_opacity(0.62),
            FadeOut(scrim_n),
        )
        nand["all"].set_z_index(2)

        # STM: compressed but continuous scan, finishing at F10413 (NB14).
        scrim_s = spotlight_scrim()
        arrow_s = make_source_arrow(CYAN).set_z_index(24)
        self.add(scrim_s)
        self.play_through(10290, scrim_s.animate.set_fill(opacity=0.76), Create(arrow_s[0]), FadeIn(arrow_s[1], scale=0.5))
        stm = make_stm()
        stm["all"].set_z_index(22)
        self.play_through(10320, FadeIn(stm["title"]), FadeIn(stm["sample"]), FadeIn(stm["tip_group"]), FadeIn(stm["meter"]))
        scan_right = stm["tip_group"].copy().shift(RIGHT * 1.45 + UP * 0.10)
        bar_high = stm["bar"].copy().stretch_to_fit_height(2.85).move_to([stm["bar_x"], stm["bar_bottom"] + 1.425, 0])
        value_high = txt("I = 0.812 nA", 25, YELLOW, font="Courier New").move_to([stm["bar_x"], stm["bar_bottom"] + stm["bar_max_h"] + 0.80, 0])
        self.play_through(10362, Transform(stm["tip_group"], scan_right), Transform(stm["bar"], bar_high), Transform(stm["value"], value_high), rate_func=linear)
        scan_left = stm["tip_group"].copy().shift(LEFT * 2.35 + DOWN * 0.16)
        bar_low = stm["bar"].copy().stretch_to_fit_height(0.52).move_to([stm["bar_x"], stm["bar_bottom"] + 0.26, 0])
        value_low = txt("I = 0.147 nA", 25, YELLOW, font="Courier New").move_to([stm["bar_x"], stm["bar_bottom"] + stm["bar_max_h"] + 0.80, 0])
        self.play_through(10390, Transform(stm["tip_group"], scan_left), Transform(stm["bar"], bar_low), Transform(stm["value"], value_low), rate_func=linear)
        self.play_through(
            10413,
            FadeOut(arrow_s),
            stm["all"].animate.scale(INTERMEDIATE_APP_SCALES[1]).move_to(APP_DOCKS[1]).set_opacity(0.62),
            FadeOut(scrim_s),
        )
        stm["all"].set_z_index(2)

        # CMOS: professional gate/oxide/current symbols; no meaningless cell numbers.
        scrim_c = spotlight_scrim()
        arrow_c = make_source_arrow(RED).set_z_index(24)
        self.add(scrim_c)
        self.play_through(10440, scrim_c.animate.set_fill(opacity=0.76), Create(arrow_c[0]), FadeIn(arrow_c[1], scale=0.5))
        cmos = make_cmos()
        cmos["all"].set_z_index(22)
        self.play_through(10475, FadeIn(cmos["title"]), Create(cmos["rails"]), FadeIn(cmos["transistor"]), FadeIn(cmos["gauge"]))

        rng = np.random.default_rng(42)
        endpoints = ((4, 58, 4.0, 0.30, 10508), (3, 75, 9.0, 0.60, 10541), (2, 95, 19.0, 0.92, 10575))
        for node, temp, power, fraction, end_frame in endpoints:
            dots = VGroup()
            animations = []
            for origin in (cmos["p_oxide"].get_center(), cmos["n_oxide"].get_center()):
                for _ in range(4):
                    dot = Dot(origin, radius=0.065, color=ORANGE)
                    target = origin + np.array([rng.uniform(-0.90, 1.20), rng.uniform(-0.50, 0.50), 0])
                    dots.add(dot)
                    animations.append(dot.animate.move_to(target).set_opacity(0.0))
            self.add(dots)
            new_fill = Arc(radius=cmos["gauge_radius"], start_angle=PI, angle=-fraction * PI,
                           arc_center=cmos["gauge_center"], color=RED, stroke_width=14)
            new_stats = cmos["stats_group"](node, temp, power).shift(STAGE_SHIFT)
            self.play_through(end_frame, AnimationGroup(*animations, lag_ratio=0.04),
                              Transform(cmos["gauge_fill"], new_fill), Transform(cmos["stats"], new_stats))
            self.remove(dots)

        glow = Circle(radius=2.40, color=RED, fill_color=RED, fill_opacity=0.06, stroke_width=0).move_to(cmos["transistor"].get_center())
        self.add(glow)
        self.play_through(10605, glow.animate.set_fill(opacity=0.20), rate_func=there_and_back)
        self.play_through(
            10637,
            FadeOut(VGroup(glow, arrow_c)),
            cmos["all"].animate.scale(INTERMEDIATE_APP_SCALES[2]).move_to(APP_DOCKS[2]).set_opacity(0.62),
            FadeOut(scrim_c),
        )
        cmos["all"].set_z_index(2)

        # F10638 starts the final re-layout; three arrows occupy exactly 2 s.
        docked = [nand["all"], stm["all"], cmos["all"]]
        self.play_through(10675, projection.animate.set_opacity(0.70), *[mob.animate.set_opacity(0.78) for mob in docked])
        projection_final = projection.copy().scale(0.853).move_to(FINAL_TUNNEL)
        docked_final = [
            mob.copy().scale(scale_factor).move_to(target)
            for mob, target, scale_factor in zip(docked, FINAL_APPS, FINAL_APP_SCALE_FACTORS)
        ]
        arrows = VGroup(
            CurvedArrow(projection_final.get_bottom() + LEFT * 0.34, docked_final[0].get_top() + UP * 0.04,
                        angle=-0.30, color=ORANGE, stroke_width=3.2, tip_length=0.18),
            Arrow(projection_final.get_bottom(), docked_final[1].get_top() + UP * 0.04,
                  buff=0.08, color=CYAN, stroke_width=3.2, tip_length=0.18),
            CurvedArrow(projection_final.get_bottom() + RIGHT * 0.34, docked_final[2].get_top() + UP * 0.04,
                        angle=0.30, color=RED, stroke_width=3.2, tip_length=0.18),
        ).set_z_index(30)
        self.play_through(
            10720,
            projection.animate.scale(0.853).move_to(FINAL_TUNNEL).set_opacity(0.92),
            *[
                mob.animate.scale(scale_factor).move_to(target).set_opacity(0.88)
                for mob, target, scale_factor in zip(docked, FINAL_APPS, FINAL_APP_SCALE_FACTORS)
            ],
            Create(arrows[0]),
        )
        # First arrow begins at F10676; the sequence finishes at F10795.
        self.play_through(GLOBAL_END, LaggedStart(Create(arrows[1]), Create(arrows[2]), lag_ratio=0.32), rate_func=ease_out_cubic)

        if self.cursor != GLOBAL_END - GLOBAL_START + 1:
            raise RuntimeError(f"Expected 1087 frames, built {self.cursor}")


if __name__ == "__main__":
    print("Render TunnellingApplicationsVoiceV9 with Manim CE.")
