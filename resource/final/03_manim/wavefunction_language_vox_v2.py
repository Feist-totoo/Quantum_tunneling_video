"""Voice-aligned particle-to-wavefunction chapter.

Global timeline: F03878-F05544 (1667 frames, 1920x1080, 60 fps).
NB08-NB11 are retained as semantic action nodes while every spoken cue is
timed in the source animation rather than stretched later in Resolve.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np

from manim import *
from manim.utils.rate_functions import ease_in_out_cubic, ease_in_out_sine


BG = "#000000"
WHITE_C = "#F4F4F4"
GREY = "#7B8794"
CYAN = "#58C4DD"
CYAN_LIGHT = "#8AEAFF"
RED = "#FC6255"
PURPLE = "#9A72AC"
ORANGE = "#FF862F"
YELLOW = "#FFFF00"
GREEN = "#5CD0B3"
FONT = "Noto Sans SC"
FPS = 60
PROJECT_ROOT = Path(__file__).resolve().parents[4]
PORTRAIT = PROJECT_ROOT / "resource" / "final" / "04_source_images" / "people" / "erwin_schrodinger_vox_cutout_v2.png"

config.background_color = BG
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = FPS


def zh(text: str, size: int, color: str = WHITE_C, weight: str = "NORMAL") -> Text:
    return Text(text, font=FONT, font_size=size, color=color, weight=weight)


def scientist_block() -> tuple[ImageMobject, Rectangle, VMobject, Text, Text]:
    # 80% of the old portrait size and 50 px lower, matching the Heisenberg card.
    image = ImageMobject(str(PORTRAIT)).set_height(4.52).move_to([5.03, -0.49, 0]).set_opacity(0.62)
    wash = Rectangle(width=3.02, height=4.70, fill_color=CYAN, fill_opacity=0.045, stroke_width=0).move_to(image)
    leader = VMobject(color=CYAN, stroke_width=2.4)
    leader.set_points_as_corners([
        [3.88, -1.54, 0], [3.50, -1.54, 0], [3.12, -2.17, 0], [1.10, -2.17, 0]
    ])
    name_year = zh("薛定谔  ·  1887—1961", 27, CYAN, "BOLD")
    name_year.next_to(leader.get_end(), UP, buff=0.10).align_to(leader.get_end(), LEFT)
    work = zh("《量子化是一个本征值问题》 · 1926", 19, GREY)
    work.next_to(name_year, DOWN, buff=0.08).align_to(name_year, LEFT)
    return image, wash, leader, name_year, work


class WavefunctionLanguageVoxV2(Scene):
    """Exact 1667-frame source segment for Resolve."""

    def play_frames(self, *animations: Animation, frames: int, rate_func=smooth) -> None:
        self.play(*animations, run_time=frames / FPS, rate_func=rate_func)

    def wait_frames(self, frames: int) -> None:
        self.wait(frames / FPS)

    def construct(self) -> None:
        self.camera.background_color = BG

        # F03878-F04060 (local 0-182): a single negative particle, NB08.
        halo = Circle(radius=0.60, color=CYAN, stroke_width=2.0, stroke_opacity=0.28)
        core = Dot(radius=0.34, color=CYAN_LIGHT, fill_opacity=0.96)
        minus = MathTex(r"-", font_size=44, color=BG).move_to(core)
        electron = VGroup(halo, core, minus)
        guide = Line([-2.9, 0, 0], [2.9, 0, 0], color=GREY, stroke_width=1.2, stroke_opacity=0.28)
        self.play_frames(FadeIn(guide), FadeIn(electron, scale=0.72), frames=36)
        self.play_frames(electron.animate.shift(RIGHT * 0.34).scale(1.08), frames=87, rate_func=ease_in_out_sine)
        self.wait_frames(60)

        # F04061-F04256 (local 183-378): preserve the macroscopic point/sphere model.
        orbit = Circle(radius=1.05, color=CYAN, stroke_width=1.5, stroke_opacity=0.16)
        cross = VGroup(
            Line(LEFT * 1.36, RIGHT * 1.36, color=GREY, stroke_width=1.0, stroke_opacity=0.30),
            Line(DOWN * 1.36, UP * 1.36, color=GREY, stroke_width=1.0, stroke_opacity=0.30),
        )
        point_model = VGroup(orbit, cross)
        self.play_frames(Create(point_model), Indicate(electron, color=WHITE_C, scale_factor=1.10), frames=60)
        self.play_frames(
            electron.animate.move_to([-2.30, 0.34, 0]).scale(0.84),
            point_model.animate.move_to([-2.30, 0.34, 0]).scale(0.84),
            guide.animate.set_opacity(0.08), frames=136, rate_func=ease_in_out_cubic,
        )

        # F04257-F04335 (local 379-457): Schrödinger card steps into view.
        portrait, wash, leader, name_year, work = scientist_block()
        self.play_frames(
            FadeIn(wash), FadeIn(portrait, shift=LEFT * 0.16),
            LaggedStart(Create(leader), FadeIn(name_year, shift=RIGHT * 0.10), FadeIn(work, shift=RIGHT * 0.10), lag_ratio=0.24),
            frames=79,
        )

        # F04336-F04447 (local 458-569): particle changes continuously into a wave packet, NB09.
        axes = Axes(
            x_range=[-5, 5, 1], y_range=[-1.45, 1.55, 0.5], x_length=7.35, y_length=3.15,
            tips=False, axis_config={"color": GREY, "stroke_width": 1.55},
        ).move_to([-2.15, 0.38, 0])
        phase = ValueTracker(0.0)
        env = lambda x: np.exp(-0.24 * x * x)
        re_curve = always_redraw(lambda: axes.plot(
            lambda x: env(x) * np.cos(3.3 * x - phase.get_value()), x_range=[-5, 5], color=RED, stroke_width=3.1,
        ))
        im_curve = always_redraw(lambda: axes.plot(
            lambda x: env(x) * np.sin(3.3 * x - phase.get_value()), x_range=[-5, 5], color=CYAN, stroke_width=3.1,
        ))
        self.play_frames(
            Create(axes), FadeIn(re_curve), FadeIn(im_curve),
            FadeOut(electron, scale=0.36), FadeOut(point_model, scale=0.60), FadeOut(guide),
            frames=112, rate_func=ease_in_out_cubic,
        )

        # F04448-F04593 (local 570-715): identify the wave-packet components.
        labels = VGroup(
            MathTex(r"\mathrm{Re}\,\psi", color=RED, font_size=34),
            MathTex(r"\mathrm{Im}\,\psi", color=CYAN, font_size=34),
        ).arrange(RIGHT, buff=1.1).next_to(axes, DOWN, buff=0.13)
        self.play_frames(FadeIn(labels, shift=UP * 0.10), phase.animate.set_value(TAU), frames=146, rate_func=ease_in_out_sine)

        # F04594-F04740 (local 716-862): the wavefunction state notation.
        wave_equation = MathTex(
            r"\psi=\mathrm{Re}\,\psi+i\,\mathrm{Im}\,\psi",
            font_size=40, color=WHITE_C,
        ).move_to([2.20, 1.72, 0])
        wave_equation.set_color_by_tex("Re", RED)
        wave_equation.set_color_by_tex("Im", CYAN)
        wave_equation.set_color_by_tex(r"\psi", PURPLE)
        self.play_frames(Write(wave_equation), phase.animate.set_value(TAU * 1.72), frames=147, rate_func=ease_in_out_sine)

        # F04741-F04946 (local 863-1068): modulus squared maps to probability density.
        mapping = MathTex(
            r"|\psi|^2=(\mathrm{Re}\,\psi)^2+(\mathrm{Im}\,\psi)^2",
            font_size=35, color=WHITE_C,
        ).move_to([2.18, 0.84, 0])
        mapping.set_color_by_tex("Re", RED)
        mapping.set_color_by_tex("Im", CYAN)
        mapping.set_color_by_tex(r"\psi", PURPLE)
        rho = axes.plot(lambda x: env(x) ** 2, x_range=[-5, 5], color=PURPLE, stroke_width=5.5)
        rho_label = MathTex(r"\rho(x)=|\psi(x)|^2", color=PURPLE, font_size=34).next_to(axes, UP, buff=0.12)
        self.play_frames(
            Write(mapping), FadeIn(rho_label), Create(rho), phase.animate.set_value(TAU * 2.70),
            frames=206, rate_func=ease_in_out_sine,
        )

        # F04947-F05201 (local 1069-1323): clear portrait/plots and move the
        # wavefunction to the top before deriving the stationary equation, NB10.
        scientist = Group(portrait, wash, leader, name_year, work)
        plot_layer = Group(axes, re_curve, im_curve, labels, mapping, rho, rho_label)
        self.play_frames(
            FadeOut(scientist), FadeOut(plot_layer),
            wave_equation.animate.scale(0.86).to_edge(UP, buff=0.26), frames=45,
        )
        stationary = MathTex(
            r"-\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2}",
            r"+V(x)\psi",
            r"=E\psi",
            font_size=54,
        ).move_to([0, 0.78, 0])
        stationary[0].set_color(PURPLE)
        stationary[1].set_color(ORANGE)
        stationary[2].set_color(YELLOW)
        self.play_frames(Write(stationary), frames=150)
        self.play_frames(Indicate(stationary, color=WHITE_C, scale_factor=1.035), frames=60)

        # F05202-F05369 (local 1324-1491): V(x) is the environment; flash it once.
        potential_axis = Axes(
            x_range=[-4, 4, 1], y_range=[0, 3.2, 1], x_length=7.3, y_length=2.35,
            tips=False, axis_config={"color": GREY, "stroke_width": 1.35},
        ).shift(DOWN * 1.47)
        potential_floor = potential_axis.plot(lambda x: 0.45 + 0.11 * np.cos(0.8 * x), x_range=[-4, 4], color=ORANGE, stroke_width=3.4)
        v_label = MathTex(r"V(x)", color=ORANGE, font_size=34).next_to(potential_axis, LEFT, buff=0.10)
        self.play_frames(Create(potential_axis), Create(potential_floor), FadeIn(v_label), frames=96)
        self.play_frames(Indicate(stationary[1], color=WHITE_C, scale_factor=1.15), Indicate(v_label, color=WHITE_C, scale_factor=1.15), frames=48)
        self.wait_frames(24)

        # F05370-F05539 (local 1492-1661): build several potential fields, NB11.
        self.play_frames(FadeOut(VGroup(potential_axis, potential_floor, v_label)), frames=20)
        families = VGroup()
        definitions = (("well", CYAN), ("oscillator", PURPLE), ("barrier", ORANGE))
        for idx, (_, color) in enumerate(definitions):
            ax = Axes(
                x_range=[-2, 2, 1], y_range=[0, 3, 1], x_length=3.55, y_length=2.36,
                tips=False, axis_config={"color": GREY, "stroke_width": 1.35},
            )
            if idx == 0:
                graph = VGroup(
                    Line(ax.c2p(-1.35, 0), ax.c2p(-1.35, 2.65), color=color, stroke_width=5),
                    Line(ax.c2p(-1.35, 0), ax.c2p(1.35, 0), color=color, stroke_width=5),
                    Line(ax.c2p(1.35, 0), ax.c2p(1.35, 2.65), color=color, stroke_width=5),
                )
            elif idx == 1:
                graph = ax.plot(lambda x: 0.58 * x * x, x_range=[-1.9, 1.9], color=color, stroke_width=5)
            else:
                graph = VGroup(
                    Line(ax.c2p(-0.62, 0), ax.c2p(-0.62, 2.35), color=color, stroke_width=5),
                    Line(ax.c2p(-0.62, 2.35), ax.c2p(0.62, 2.35), color=color, stroke_width=5),
                    Line(ax.c2p(0.62, 2.35), ax.c2p(0.62, 0), color=color, stroke_width=5),
                )
            families.add(VGroup(ax, graph))
        families.arrange(RIGHT, buff=0.55).shift(DOWN * 1.40)
        self.play_frames(LaggedStart(*[FadeIn(group, shift=UP * 0.22) for group in families], lag_ratio=0.22), frames=110)
        barrier_focus = SurroundingRectangle(families[2], color=ORANGE, buff=0.14, stroke_width=2.6)
        self.play_frames(Create(barrier_focus), Indicate(families[2], color=WHITE_C, scale_factor=1.035), frames=40)

        # F05540-F05544: five-frame visual handle for the Blender transition.
        self.wait_frames(5)


if __name__ == "__main__":
    print("Render WavefunctionLanguageVoxV2 with the Manim CLI.")
