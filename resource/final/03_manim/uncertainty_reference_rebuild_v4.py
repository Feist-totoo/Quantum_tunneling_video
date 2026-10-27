"""Voice-aligned uncertainty-principle chapter.

Global timeline: F02769-F03877 (1109 frames, 1920x1080, 60 fps).
The first 545 local frames introduce the relation and Heisenberg. At F03314
the relation settles into the lower-right corner and remains visible while
NB06 starts the paired position/momentum demonstration; NB07 lands on the
last frame. All stochastic samples are deterministic and seek-safe.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np

from manim import *
from manim.utils.rate_functions import ease_in_out_sine


BG = "#000000"
WHITE = "#F4F4F4"
AXIS = "#8A97A8"
CYAN = "#58C4DD"
CYAN_GLOW = "#8AEAFF"
RED = "#FC6255"
RED_GLOW = "#FF9A8E"
PURPLE = "#9A72AC"
ORANGE = "#FF862F"
DIVIDER = "#202934"
FONT = "Noto Sans SC"
FPS = 60
PROJECT_ROOT = Path(__file__).resolve().parents[4]
PORTRAIT = PROJECT_ROOT / "resource" / "final" / "04_source_images" / "people" / "werner_heisenberg_vox_cutout_v2.png"

config.background_color = BG
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = FPS


def horizontal_axis(y: float, label_text: str, accent_color: str) -> VGroup:
    baseline = Arrow(
        [-6.45, y, 0], [6.18, y, 0], buff=0, color=AXIS,
        stroke_width=1.65, tip_length=0.16,
    )
    ticks = VGroup(*[
        Line([x, y - 0.105, 0], [x, y + 0.105, 0], color=AXIS, stroke_width=1.15)
        for x in np.linspace(-5.35, 5.05, 11)
    ])
    y_axis = Arrow(
        [-6.30, y - 0.48, 0], [-6.30, y + 0.55, 0], buff=0,
        color=AXIS, stroke_width=1.45, tip_length=0.13,
    )
    label = Text(label_text, font=FONT, font_size=25, color=WHITE).move_to([5.28, y + 0.31, 0])
    accent = Line([-6.15, y, 0], [5.58, y, 0], color=accent_color, stroke_width=1.25, stroke_opacity=0.58)
    return VGroup(baseline, ticks, y_axis, label, accent)


def wave_curve(center_y: float, sigma: float, color: str, carrier: float, amplitude: float, phase: float) -> VMobject:
    xs = np.linspace(-5.95, 4.92, 520)
    envelope = np.exp(-0.5 * (xs / max(sigma, 0.16)) ** 2)
    ys = center_y + amplitude * envelope * np.cos(carrier * xs - phase)
    curve = VMobject(color=color, stroke_width=2.7)
    curve.set_points_smoothly(np.column_stack((xs, ys, np.zeros_like(xs))))
    return curve


def sigma_markup(kind: str, color: str, font_size: int = 22) -> MarkupText:
    return MarkupText(
        f'2σ<span rise="-4100" size="62%">{kind}</span>',
        font=FONT, font_size=font_size, color=color,
    )


def scientist_block() -> tuple[ImageMobject, VMobject, Text, Text]:
    # 80% of the previous portrait height and 50 px lower at 1080p.
    portrait = ImageMobject(str(PORTRAIT)).set_height(3.88).move_to([5.05, -0.37, 0]).set_opacity(0.56)
    leader = VMobject(color=RED, stroke_width=2.4)
    leader.set_points_as_corners([
        [4.00, -1.48, 0], [3.58, -1.48, 0], [3.20, -2.13, 0], [1.42, -2.13, 0]
    ])
    name_year = Text("海森堡  ·  1901—1976", font=FONT, font_size=27, color=RED, weight="BOLD")
    name_year.next_to(leader.get_end(), UP, buff=0.10).align_to(leader.get_end(), LEFT)
    work = Text("《量子论运动学与力学的直观内容》 · 1927", font=FONT, font_size=19, color=AXIS)
    work.next_to(name_year, DOWN, buff=0.08).align_to(name_year, LEFT)
    return portrait, leader, name_year, work


class UncertaintyReferencesStacked(Scene):
    """Exact 1109-frame source segment for Resolve."""

    def play_frames(self, *animations: Animation, frames: int, rate_func=smooth) -> None:
        self.play(*animations, run_time=frames / FPS, rate_func=rate_func)

    def wait_frames(self, frames: int) -> None:
        self.wait(frames / FPS)

    def construct(self) -> None:
        self.camera.background_color = BG

        # F02769-F02947 (local 0-178): the uncertainty relation owns the frame.
        relation = MathTex(r"\sigma_x\,\sigma_p\geq\frac{\hbar}{2}", font_size=92, color=WHITE)
        relation.set_color_by_tex(r"\sigma_x", CYAN)
        relation.set_color_by_tex(r"\sigma_p", RED)
        relation.set_color_by_tex(r"\hbar", PURPLE)
        relation_glow = SurroundingRectangle(relation, color=PURPLE, buff=0.30, stroke_width=2.0, stroke_opacity=0.28)
        self.play_frames(FadeIn(relation, scale=0.92), Create(relation_glow), frames=30)
        self.play_frames(Indicate(relation, color=WHITE, scale_factor=1.06), frames=36)
        self.wait_frames(113)

        # F02948-F03065 (local 179-296): Heisenberg and horizontal metadata.
        portrait, leader, name_year, work = scientist_block()
        self.play_frames(
            relation.animate.scale(0.82).move_to([-1.52, 1.35, 0]),
            relation_glow.animate.scale(0.82).move_to([-1.52, 1.35, 0]),
            FadeIn(portrait, shift=LEFT * 0.16), frames=34,
        )
        self.play_frames(
            LaggedStart(Create(leader), FadeIn(name_year, shift=RIGHT * 0.12), FadeIn(work, shift=RIGHT * 0.12), lag_ratio=0.28),
            frames=84,
        )

        # F03066-F03208 (local 297-439): non-commuting operators imply the bound.
        commutator = MathTex(r"[\hat{x},\hat{p}]=i\hbar", font_size=57, color=WHITE).move_to([-1.52, -0.08, 0])
        commutator.set_color_by_tex(r"\hat{x}", CYAN)
        commutator.set_color_by_tex(r"\hat{p}", RED)
        implication = MathTex(r"\Longrightarrow", font_size=48, color=ORANGE).move_to([-1.52, 0.60, 0])
        self.play_frames(Write(commutator), FadeIn(implication, shift=UP * 0.08), frames=70)
        self.play_frames(
            Indicate(commutator, color=ORANGE, scale_factor=1.055),
            Indicate(relation, color=PURPLE, scale_factor=1.045), frames=43,
        )
        self.wait_frames(30)

        # F03209-F03313 (local 440-544): statistical interpretation. During
        # the transition, retire the portrait and derivation while preserving
        # the uncertainty relation as a compact lower-right reference.
        variance = MathTex(r"\sigma_x^2=\langle(x-\langle x\rangle)^2\rangle", font_size=40, color=CYAN).move_to([-1.52, -1.02, 0])
        self.play_frames(FadeIn(variance, shift=UP * 0.12), frames=45)
        self.wait_frames(30)
        retiring_intro = Group(relation_glow, portrait, leader, name_year, work, commutator, implication, variance)
        relation.set_z_index(20)
        self.play_frames(
            FadeOut(retiring_intro),
            relation.animate.scale(0.55).move_to([5.28, -3.05, 0]).set_opacity(0.92),
            frames=30,
            rate_func=ease_in_out_sine,
        )

        # NB06-NB07, F03314-F03877 (local 545-1108).
        sigma_x = ValueTracker(2.10)
        motion_clock = ValueTracker(0.0)
        motion_clock.add_updater(lambda tracker, dt: tracker.increment_value(dt))
        self.add(motion_clock)

        def sigma_k() -> float:
            return float(np.clip(1.42 / sigma_x.get_value(), 0.42, 3.70))

        position_y = 3.08
        frequency_y = 1.25
        lower_y = -1.70
        position_axis = horizontal_axis(position_y, "Position", CYAN)
        frequency_axis = horizontal_axis(frequency_y, "Spatial frequency", RED)
        divider = Line([-6.75, 0.15, 0], [6.75, 0.15, 0], color=DIVIDER, stroke_width=1.0)
        lower_axis = Line([-6.22, lower_y, 0], [6.18, lower_y, 0], color=DIVIDER, stroke_width=1.4)

        position_wave = always_redraw(lambda: wave_curve(
            position_y, 1.16 * sigma_x.get_value(), CYAN, 6.15, 0.43, 1.42 * motion_clock.get_value()
        ))
        frequency_wave = always_redraw(lambda: wave_curve(
            frequency_y, 1.20 * sigma_k(), RED, 6.15, 0.43, -1.72 * motion_clock.get_value()
        ))

        def position_samples() -> VGroup:
            frame_index = int(np.floor(motion_clock.get_value() * FPS + 1e-6))
            rng = np.random.default_rng(1907 + frame_index)
            sample_z = np.clip(rng.normal(0.0, 1.0, 38), -2.70, 2.70)
            width_now = 0.88 * sigma_x.get_value()
            dots = VGroup()
            for z in sample_z:
                x = float(np.clip(-1.02 + z * width_now, -6.02, 5.75))
                y = lower_y + float(np.clip(rng.normal(0.0, 0.085), -0.18, 0.18))
                density = float(np.exp(-0.50 * z * z))
                opacity = float(np.clip(0.18 + 0.62 * density + rng.normal(0.0, 0.08), 0.16, 0.88))
                radius = float(np.clip(rng.normal(0.052, 0.010), 0.034, 0.071))
                point = [x, y, 0]
                dots.add(
                    Dot(point, radius=radius * 2.05, color=CYAN, fill_opacity=0.095 * opacity, stroke_width=0),
                    Dot(point, radius=radius, color=CYAN_GLOW, fill_opacity=opacity, stroke_width=0),
                )
            return dots

        def momentum_arrows() -> VGroup:
            frame_index = int(np.floor(motion_clock.get_value() * FPS + 1e-6))
            rng = np.random.default_rng(8111 + frame_index)
            spread = sigma_k()
            arrows = VGroup()
            for _ in range(12):
                start_x = -1.22 + float(np.clip(rng.normal(0.0, 0.18), -0.36, 0.36))
                length = float(np.clip(rng.normal(0.78 + 0.56 * spread, 0.24 * spread), 0.32, 3.85))
                direction = -1.0 if rng.random() < 0.22 else 1.0
                opacity = float(rng.uniform(0.30, 0.76))
                start = [start_x, lower_y, 0]
                end = [start_x + direction * length, lower_y, 0]
                arrows.add(
                    Arrow(start, end, buff=0, color=RED_GLOW, stroke_width=6.4, stroke_opacity=0.10 * opacity, tip_length=0.18),
                    Arrow(start, end, buff=0, color=RED, stroke_width=2.25, stroke_opacity=opacity, tip_length=0.15),
                )
            return arrows

        position_dots = always_redraw(position_samples)
        momentum_vectors = always_redraw(momentum_arrows)
        position_brace = always_redraw(lambda: BraceBetweenPoints(
            [-1.02 - 1.72 * sigma_x.get_value(), lower_y - 0.34, 0],
            [-1.02 + 1.72 * sigma_x.get_value(), lower_y - 0.34, 0],
            direction=DOWN, color=CYAN, stroke_width=1.6,
        ))
        position_label = always_redraw(lambda: sigma_markup("position", CYAN).next_to(position_brace, DOWN, buff=0.06))
        momentum_brace = always_redraw(lambda: BraceBetweenPoints(
            [-1.36, lower_y + 0.42, 0], [-1.36 + 1.74 + 1.20 * sigma_k(), lower_y + 0.42, 0],
            direction=UP, color=RED, stroke_width=1.6,
        ))
        momentum_label = always_redraw(lambda: sigma_markup("momentum", RED).next_to(momentum_brace, UP, buff=0.06))

        axes_group = VGroup(position_axis, frequency_axis, divider, lower_axis)
        live_group = VGroup(position_wave, frequency_wave, position_dots, momentum_vectors, position_brace, position_label, momentum_brace, momentum_label)
        self.play_frames(
            LaggedStart(*[Create(item) for item in axes_group], lag_ratio=0.10),
            FadeIn(live_group), frames=50,
        )
        self.play_frames(sigma_x.animate.set_value(2.90), frames=140, rate_func=ease_in_out_sine)
        self.play_frames(sigma_x.animate.set_value(0.72), frames=132, rate_func=ease_in_out_sine)
        self.play_frames(sigma_x.animate.set_value(1.55), frames=80, rate_func=ease_in_out_sine)
        self.play_frames(sigma_x.animate.set_value(0.46), frames=90, rate_func=ease_in_out_sine)
        self.play_frames(sigma_x.animate.set_value(2.42), frames=72, rate_func=ease_in_out_sine)


if __name__ == "__main__":
    print("Render UncertaintyReferencesStacked with the Manim CLI.")
