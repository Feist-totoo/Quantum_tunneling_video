"""Voice-aligned NB12 with a standard SIS Josephson junction.

Global timeline F09123-F09708 inclusive (586 frames at 60 fps).  The main
model is a superconductor-insulator-superconductor stack.  The former NB13
macro-circuit, laureates and quantised levels pop into a reduced right-hand
stage instead of replacing the junction model.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
from manim import *
from manim.utils.rate_functions import ease_in_out_cubic, ease_out_cubic, ease_out_back

from macro_circuit_transition_v2 import perspective_speed_lines, portrait_card, slab
from macro_circuit_transition_v1 import circuit_model
from tunneling_applications_resolve_v8 import make_tunnel_source


ROOT = Path(__file__).resolve().parents[4]
BLENDER_END = ROOT / "resource" / "final" / "04_source_images" / "science_references" / "blender_v5_f3578_transition_source.png"

FPS = 60
GLOBAL_START = 9123
GLOBAL_END = 9708

BG = "#000000"
WHITE_C = "#F4F4F4"
GREY = "#74808D"
DARK = "#07121B"
CYAN = "#58C4DD"
CYAN_LIGHT = "#8AEAFF"
BLUE = "#2459A8"
BLUE_DARK = "#123A70"
YELLOW = "#FFFF00"
ORANGE = "#FF862F"
ORANGE_DARK = "#B94B24"
PURPLE = "#9A72AC"
RED = "#FC6255"
FONT = "Noto Sans SC"

config.background_color = BG
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = FPS


def txt(value: str, size: int, color: str = WHITE_C, weight: str = "NORMAL") -> Text:
    return Text(value, font=FONT, font_size=size, color=color, weight=weight)


def sis_josephson_model() -> dict[str, Mobject]:
    """Build a readable S-I-S sandwich with two electrodes and one insulator."""
    skew = np.array([0.92, 0.56, 0.0])
    x0, x1 = -3.15, 1.20

    def footprint(y: float) -> list[np.ndarray]:
        return [
            np.array([x0, y, 0.0]),
            np.array([x1, y, 0.0]),
            np.array([x1, y, 0.0]) + skew,
            np.array([x0, y, 0.0]) + skew,
        ]

    lower = slab(footprint(-1.30), depth=0.34, top=BLUE, side=BLUE_DARK, stroke=CYAN_LIGHT)
    insulator = slab(footprint(-0.94), depth=0.14, top=ORANGE, side=ORANGE_DARK, stroke="#FFB47A")
    upper = slab(footprint(-0.60), depth=0.34, top="#2E67BC", side=BLUE_DARK, stroke=CYAN_LIGHT)

    lower_tag = VGroup(MathTex(r"S_1", color=CYAN_LIGHT, font_size=30), txt("超导电极", 18, CYAN_LIGHT)).arrange(RIGHT, buff=0.10).move_to([-1.02, -1.49, 0])
    barrier_tag = VGroup(MathTex("I", color=ORANGE, font_size=29), txt("绝缘层", 18, ORANGE)).arrange(RIGHT, buff=0.10).move_to([-1.02, -1.00, 0])
    upper_tag = VGroup(MathTex(r"S_2", color=CYAN_LIGHT, font_size=30), txt("超导电极", 18, CYAN_LIGHT)).arrange(RIGHT, buff=0.10).move_to([-1.02, -0.70, 0])

    phase_lower = MathTex(r"\Delta e^{-i\phi/2}", color=CYAN_LIGHT, font_size=30).move_to([-1.35, -1.08, 0])
    phase_upper = MathTex(r"\Delta e^{i\phi/2}", color=CYAN_LIGHT, font_size=30).move_to([0.10, -0.18, 0])

    width_arrow = DoubleArrow([2.34, -1.05, 0], [2.34, -0.80, 0], buff=0.01,
                              color=WHITE_C, stroke_width=2.2, tip_length=0.10)
    width_label = MathTex(r"W_I", color=WHITE_C, font_size=27).next_to(width_arrow, RIGHT, buff=0.08)

    lower_pair = VGroup(Dot([-0.63, -1.05, 0], radius=0.085, color=RED),
                        Dot([-0.43, -1.02, 0], radius=0.085, color=RED))
    upper_pair = lower_pair.copy().shift(UP * 0.72).set_opacity(0.48)
    tunnel_arrow = Arrow(lower_pair.get_top() + UP * 0.02, upper_pair.get_bottom() + DOWN * 0.02,
                         buff=0.02, color=RED, stroke_width=3.0, tip_length=0.16)
    pair_label = MathTex(r"2e", color=RED, font_size=26).next_to(tunnel_arrow, RIGHT, buff=0.08)

    sis_tag = MathTex(r"S_1\,-\,I\,-\,S_2", color=WHITE_C, font_size=34).move_to([-0.58, 1.56, 0])
    model = VGroup(lower, insulator, upper, lower_tag, barrier_tag, upper_tag,
                   phase_lower, phase_upper, width_arrow, width_label,
                   lower_pair, upper_pair, tunnel_arrow, pair_label, sis_tag)
    model.move_to([-0.60, -0.02, 0]).scale(1.04)
    weak_link = VGroup(insulator, barrier_tag, width_arrow, width_label, lower_pair, upper_pair, tunnel_arrow, pair_label)
    return {"all": model, "weak_link": weak_link, "arrow": tunnel_arrow}


class MacroCircuitTransitionVoiceV3(Scene):
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

        blender = ImageMobject(str(BLENDER_END)).set_height(config.frame_height)
        blender.align_to(LEFT * config.frame_width / 2, LEFT)
        self.add(blender)
        self.wait_to(9135)

        target = np.array([-1.05, -0.08, 0.0])
        line_reveal = ValueTracker(0.0)
        line_rotation = ValueTracker(0.0)
        line_opacity = ValueTracker(0.34)
        speed_lines = always_redraw(
            lambda: perspective_speed_lines(target, line_reveal.get_value(), line_rotation.get_value(), line_opacity.get_value())
        )
        self.add(speed_lines)
        self.play_through(9137, line_reveal.animate.set_value(0.18), rate_func=ease_out_cubic)

        junction = sis_josephson_model()
        model = junction["all"]
        model.save_state()
        model.scale(3.35).set_opacity(0.0)
        self.add(model)
        self.play_through(
            9224,
            blender.animate.scale(0.045).move_to(target).set_opacity(0.04),
            line_reveal.animate.set_value(1.0),
            line_rotation.animate.set_value(-5 * DEGREES),
            Restore(model),
            rate_func=ease_out_cubic,
        )
        self.play_through(9250, blender.animate.set_opacity(0), line_opacity.animate.set_value(0),
                          model.animate.scale(1.035), rate_func=ease_out_back)
        self.remove(blender, speed_lines)
        self.play_through(9270, model.animate.scale(1 / 1.035), rate_func=ease_out_cubic)

        # Former NB13 becomes a reduced right-hand stage instead of replacing
        # the scientifically correct S-I-S model.
        circuit = circuit_model()
        circuit_world = circuit["all"]
        circuit_world.scale(0.47).move_to([2.25, -0.12, 0])
        circuit_frame = RoundedRectangle(corner_radius=0.16, width=4.95, height=3.95,
                                         fill_color=DARK, fill_opacity=0.94,
                                         stroke_color="#294054", stroke_width=1.8).move_to([2.25, -0.08, 0])
        macro_tag = txt("宏观电路中的量子隧穿", 19, CYAN, "BOLD").move_to([2.25, 2.10, 0])
        mini_stage = Group(circuit_frame, circuit_world, macro_tag)
        self.play_through(9308, model.animate.scale(0.74).move_to([-3.35, -0.05, 0]),
                          FadeIn(mini_stage, scale=0.68), rate_func=ease_out_back)

        portrait_items = [
            portrait_card("john_clarke_2025_official.jpg", "JOHN CLARKE", 1.48),
            portrait_card("michel_devoret_2025_official.jpg", "MICHEL DEVORET", -0.02),
            portrait_card("john_martinis_2025_official.jpg", "JOHN MARTINIS", -1.52),
        ]
        portraits = Group(*portrait_items).scale(0.57).move_to([5.38, -0.05, 0])
        nobel = txt("2025 诺贝尔物理学奖", 25, YELLOW, "BOLD").move_to([4.70, 3.22, 0])
        self.play_through(9331, FadeIn(nobel, shift=DOWN * 0.08),
                          LaggedStart(*[FadeIn(card, scale=0.68) for card in portrait_items], lag_ratio=0.16),
                          rate_func=ease_out_back)

        path_y = circuit["jj"].get_center()[1]
        current = Dot([circuit_frame.get_left()[0] + 0.40, path_y, 0], radius=0.075, color=CYAN_LIGHT)
        current_path = VMobject().set_points_as_corners([
            current.get_center(),
            circuit["jj"].get_center(),
            [circuit_frame.get_right()[0] - 0.45, path_y, 0],
        ])
        self.add(current)
        self.play_through(9500, MoveAlongPath(current, current_path), rate_func=ease_in_out_cubic)
        self.play_through(9588, FadeOut(current),
                          circuit["phase_dot"].animate.shift(UP * 0.10).scale(1.35),
                          rate_func=there_and_back)

        axes = circuit["axes"]
        levels = VGroup(*[
            DashedLine(
                [axes.get_left()[0] + 0.28, axes.get_bottom()[1] + 0.30 + 0.16 * i, 0],
                [axes.get_right()[0] - 0.22, axes.get_bottom()[1] + 0.30 + 0.16 * i, 0],
                color=CYAN if i < 2 else ORANGE, stroke_width=1.4, dash_length=0.07,
            )
            for i in range(4)
        ])
        self.play_through(9650, LaggedStart(*[Create(line) for line in levels], lag_ratio=0.18),
                          circuit["potential"].animate.shift(UP * 0.06).scale(1.025),
                          rate_func=there_and_back)

        focus = SurroundingRectangle(circuit["jj"], color=YELLOW, buff=0.10, stroke_width=2.5)
        projection_final = make_tunnel_source().scale(0.86).move_to(LEFT * 0.68)
        projection = projection_final.copy().scale(0.050).move_to(circuit["jj"]).set_opacity(0.08)
        self.add(focus, projection)
        self.play_through(
            GLOBAL_END,
            Transform(projection, projection_final),
            FadeOut(Group(model, mini_stage, portraits, nobel, levels, focus)),
            rate_func=ease_in_out_cubic,
        )
        projection.become(projection_final)

        if self.cursor != GLOBAL_END - GLOBAL_START + 1:
            raise RuntimeError(f"Expected 586 frames, built {self.cursor}")


if __name__ == "__main__":
    print("Render MacroCircuitTransitionVoiceV3 with Manim CE.")
