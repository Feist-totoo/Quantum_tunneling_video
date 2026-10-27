"""Blender-to-macroscopic-Josephson-circuit-to-2D tunnelling transition."""

from pathlib import Path
import numpy as np
from manim import *
from manim.utils.rate_functions import ease_in_out_cubic

from tunneling_applications_resolve_v8 import make_tunnel_source

ROOT = Path(__file__).resolve().parents[3]
BLENDER_END = ROOT / "renders" / "review_v3_final" / "v3_5399.png"
PEOPLE = ROOT / "remotion_project" / "public" / "assets" / "people"

BG = "#000000"
WHITE_C = "#F4F4F4"
GREY = "#74808D"
DARK = "#111923"
CYAN = "#58C4DD"
CYAN_LIGHT = "#8AEAFF"
ORANGE = "#FF862F"
YELLOW = "#FFFF00"
PURPLE = "#9A72AC"
RED = "#FC6255"
FONT = "Noto Sans SC"

config.background_color = BG
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 60


def label(text: str, size: int, color: str = WHITE_C, weight: str = "NORMAL", font: str = FONT) -> Text:
    return Text(text, font=font, font_size=size, color=color, weight=weight)


def portrait_card(filename: str, name: str, y: float) -> Group:
    image = ImageMobject(str(PEOPLE / filename)).set_height(1.30).move_to([4.42, y, 0])
    frame = RoundedRectangle(corner_radius=.10, width=1.18, height=1.42, fill_color="#0A1119", fill_opacity=1, stroke_color=CYAN, stroke_width=1.8).move_to(image)
    name_label = label(name, 18, WHITE_C, "BOLD", "Courier New").move_to([5.75, y, 0])
    return Group(frame, image, name_label)


def circuit_model() -> dict[str, Mobject]:
    chip = RoundedRectangle(corner_radius=.22, width=8.45, height=5.35, fill_color="#07121B", fill_opacity=.96, stroke_color="#294054", stroke_width=2.2).move_to([-1.75, -.05, 0])
    trace_top = Line([-5.55, 1.10, 0], [-3.22, 1.10, 0], color=CYAN, stroke_width=10)
    trace_bottom = Line([-2.18, 1.10, 0], [.64, 1.10, 0], color=CYAN, stroke_width=10)
    left_pad = RoundedRectangle(corner_radius=.09, width=1.02, height=.72, fill_color=CYAN, fill_opacity=.20, stroke_color=CYAN, stroke_width=3).move_to([-2.70, 1.10, 0])
    right_pad = left_pad.copy().move_to([-2.28, 1.10, 0])
    barrier = Rectangle(width=.10, height=.80, fill_color=ORANGE, fill_opacity=.94, stroke_width=0).move_to([-2.49, 1.10, 0])
    jj = VGroup(left_pad, right_pad, barrier)
    jj_name = label("约瑟夫森结", 21, ORANGE, "BOLD").next_to(jj, DOWN, buff=.16)

    cap_x = -.10
    cap = VGroup(
        Line([cap_x - .33, .37, 0], [cap_x - .33, 1.83, 0], color=YELLOW, stroke_width=4),
        Line([cap_x + .33, .37, 0], [cap_x + .33, 1.83, 0], color=YELLOW, stroke_width=4),
        Line([cap_x - .33, 1.10, 0], [-2.18, 1.10, 0], color=CYAN, stroke_width=3),
        Line([cap_x + .33, 1.10, 0], [.64, 1.10, 0], color=CYAN, stroke_width=3),
        MathTex("C", color=YELLOW, font_size=30).move_to([cap_x, .12, 0]),
    )
    bias = VGroup(
        Arrow([-5.52, 2.12, 0], [-3.65, 2.12, 0], buff=0, color=PURPLE, stroke_width=3, tip_length=.18),
        MathTex(r"I_{\mathrm{bias}}<I_0", color=PURPLE, font_size=29).move_to([-4.55, 2.48, 0]),
    )
    voltage = VGroup(Circle(radius=.35, color=RED, stroke_width=2.6).move_to([.66, 2.12, 0]), MathTex("V", color=RED, font_size=28).move_to([.66, 2.12, 0]), Line([.66, 1.77, 0], [.66, 1.10, 0], color=GREY, stroke_width=2))
    microwave = VMobject(color=ORANGE, stroke_width=2.6)
    xs = np.linspace(-1.55, .55, 120); ys = 2.45 + .16 * np.sin((xs + 1.55) * 13)
    microwave.set_points_smoothly(np.column_stack((xs, ys, np.zeros_like(xs))))
    microwave_lab = MathTex(r"\hbar\omega", color=ORANGE, font_size=27).next_to(microwave, UP, buff=.06)

    axes = Axes(x_range=[-2.8, 2.8, 1], y_range=[-1.8, 2.2, 1], x_length=4.55, y_length=2.10, tips=False, axis_config={"color": GREY, "stroke_width": 1.2}).move_to([-2.47, -1.45, 0])
    potential = axes.plot(lambda d: -.82 * np.cos(d) - .42 * d, x_range=[-2.65, 2.65], color=PURPLE, stroke_width=3.1)
    phase_dot = Dot(axes.c2p(-1.22, -.82 * np.cos(-1.22) - .42 * (-1.22)), radius=.095, color=YELLOW)
    tunnel_arrow = DashedLine(phase_dot.get_center(), axes.c2p(.92, -.82 * np.cos(.92) - .42 * .92), color=YELLOW, dash_length=.10, stroke_width=2.2)
    tunnel_tip = Triangle(fill_color=YELLOW, fill_opacity=1, stroke_width=0).scale(.085).rotate(-PI / 2).move_to(tunnel_arrow.get_end())
    potential_label = MathTex(r"U(\delta)", color=PURPLE, font_size=27).move_to([-5.10, -.72, 0])
    zero = label("V = 0", 19, CYAN, "BOLD", "Courier New").move_to([.05, -1.02, 0])
    escaped = label("V > 0", 19, RED, "BOLD", "Courier New").move_to([.05, -1.62, 0])
    arrow_state = Arrow([-.62, -1.02, 0], [-.62, -1.62, 0], buff=.07, color=YELLOW, stroke_width=2.4, tip_length=.16)
    model = Group(chip, trace_top, trace_bottom, jj, jj_name, cap, bias, voltage, microwave, microwave_lab, axes, potential, phase_dot, tunnel_arrow, tunnel_tip, potential_label, zero, escaped, arrow_state)
    return {"all": model, "jj": jj, "phase_dot": phase_dot, "potential": potential, "axes": axes}


class MacroCircuitTransitionV1(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        blender = ImageMobject(str(BLENDER_END)).set_width(config.frame_width)
        self.add(blender)
        self.wait(.25)

        circuit = circuit_model()
        portal_frame = RoundedRectangle(corner_radius=.05, width=1.25, height=.78, stroke_color=YELLOW, stroke_width=2.4, fill_color=BG, fill_opacity=.65).move_to(circuit["jj"])
        portal = blender.copy().set_width(1.18).move_to(portal_frame)
        portraits = Group(
            portrait_card("john_clarke_2025_official.jpg", "JOHN CLARKE", 1.63),
            portrait_card("michel_devoret_2025_official.jpg", "MICHEL DEVORET", .03),
            portrait_card("john_martinis_2025_official.jpg", "JOHN MARTINIS", -1.57),
        )
        nobel = label("2025 诺贝尔物理学奖", 28, YELLOW, "BOLD").move_to([4.72, 3.18, 0])
        macro_tag = label("宏观量子隧穿", 23, CYAN, "BOLD").move_to([-1.72, 3.17, 0])
        world = Group(circuit["all"], portal_frame, portal, macro_tag)
        world.set_opacity(0)
        self.add(world)
        self.play(blender.animate.scale(.082).move_to(circuit["jj"]).set_opacity(0), world.animate.set_opacity(1), run_time=1.80, rate_func=ease_in_out_cubic)
        self.remove(blender)
        self.play(FadeIn(portraits, shift=LEFT * .14), FadeIn(nobel, shift=DOWN * .08), run_time=.70)

        current = Dot([-5.45, 1.10, 0], radius=.09, color=CYAN_LIGHT)
        current_path = VMobject().set_points_as_corners([[-5.45, 1.10, 0], [-3.15, 1.10, 0], [-2.49, 1.10, 0], [.60, 1.10, 0]])
        self.add(current)
        self.play(MoveAlongPath(current, current_path), run_time=1.10, rate_func=ease_in_out_cubic)
        self.play(FadeOut(current), Indicate(circuit["phase_dot"], color=YELLOW, scale_factor=1.55), run_time=1.0)
        self.wait(.45)

        highlight = Circle(radius=.72, color=YELLOW, stroke_width=4).move_to(circuit["jj"])
        self.play(Create(highlight), circuit["all"].animate.set_opacity(.42), portraits.animate.set_opacity(.45), run_time=.55)
        projection_final = make_tunnel_source().scale(.86).move_to(LEFT * .68)
        projection = projection_final.copy().scale(.055).move_to(circuit["jj"]).set_opacity(.10)
        self.add(projection)
        self.play(
            Transform(projection, projection_final),
            FadeOut(Group(world, portraits, nobel)), FadeOut(highlight),
            run_time=2.10, rate_func=ease_in_out_cubic,
        )
        projection.become(projection_final)
        self.wait(1.05)


if __name__ == "__main__":
    print("Render MacroCircuitTransitionV1 with the Manim CLI.")
