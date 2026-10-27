"""Voice-aligned 660x1080 Manim right rail for the Blender tunnelling shot.

Global timeline: F05545-F09122 inclusive, 60 fps (3578 frames).
The scene is transparent and is designed to be placed against the right edge of
a 1920x1080 Resolve timeline.  It begins on geometry matching the right-most
square potential in ``wavefunction_language_vox_v2.py``.
"""

from __future__ import annotations

import math
from manim import *
from manim.utils.rate_functions import ease_in_out_cubic, ease_out_cubic


FPS = 60
GLOBAL_START = 5545
GLOBAL_END = 9122

BG = "#000000"
WHITE_C = "#F4F4F4"
GREY = "#64748B"
GRID = "#26313B"
CYAN = "#58C4DD"
CYAN_LIGHT = "#8AEAFF"
ORANGE = "#FF862F"
PURPLE = "#9A72AC"
RED = "#FC6255"
BLUE = "#4A8DFF"
YELLOW = "#FFFF00"
GREEN = "#5CD0B3"
FONT = "Noto Sans SC"

config.background_color = BG
config.transparent = True
config.pixel_width = 660
config.pixel_height = 1080
config.frame_rate = FPS
config.frame_height = 8.0
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height


def text_cn(value: str, size: int, color: str = WHITE_C, weight: str = "NORMAL") -> Text:
    return Text(value, font=FONT, font_size=size, color=color, weight=weight)


def initial_square_potential() -> VGroup:
    """Recreate the previous scene's right-most potential, pixel aligned.

    The full-frame source uses x=4.1 in a 14.222x8 frame.  A 660px right crop
    has its centre at full-frame x=4.666..., therefore the local centre is
    -0.5666... .  Y geometry is unchanged.
    """
    crop_center_x = 4.6666666667
    axis = Axes(
        x_range=[-2, 2, 1],
        y_range=[0, 3, 1],
        x_length=3.55,
        y_length=2.36,
        tips=False,
        axis_config={"color": GREY, "stroke_width": 1.35},
    )
    graph = VGroup(
        Line(axis.c2p(-0.62, 0), axis.c2p(-0.62, 2.35), color=ORANGE, stroke_width=5),
        Line(axis.c2p(-0.62, 2.35), axis.c2p(0.62, 2.35), color=ORANGE, stroke_width=5),
        Line(axis.c2p(0.62, 2.35), axis.c2p(0.62, 0), color=ORANGE, stroke_width=5),
    )
    group = VGroup(axis, graph).move_to([4.1 - crop_center_x, -1.4, 0])
    focus = SurroundingRectangle(group, color=ORANGE, buff=0.14, stroke_width=2.6)
    return VGroup(group, focus)


def barrier_dimensions(barrier: VGroup) -> VGroup:
    graph = barrier[0][1]
    left, top, right = graph[0], graph[1], graph[2]
    v_label = MathTex(r"V(x)", color=ORANGE, font_size=38).move_to([1.46, 3.18, 0])
    v_arrow = CurvedArrow(v_label.get_left() + LEFT * 0.04, top.get_center() + UP * 0.06,
                          angle=0.36, color=ORANGE, stroke_width=2.5, tip_length=0.13)
    width_arrow = DoubleArrow(left.get_bottom() + DOWN * 0.30, right.get_bottom() + DOWN * 0.30,
                              buff=0, color=PURPLE, stroke_width=2.4, tip_length=0.12)
    width_label = MathTex("W", color=PURPLE, font_size=34).next_to(width_arrow, DOWN, buff=0.06)
    height_arrow = DoubleArrow(right.get_bottom() + RIGHT * 0.34, right.get_top() + RIGHT * 0.34,
                               buff=0, color=CYAN, stroke_width=2.4, tip_length=0.12)
    height_label = MathTex(r"V_0", color=CYAN, font_size=34).next_to(height_arrow, RIGHT, buff=0.06)
    return VGroup(v_label, v_arrow, width_arrow, width_label, height_arrow, height_label)


def glow_copy(mob: Mobject, color: str) -> Mobject:
    glow = mob.copy()
    glow.set_fill(opacity=0)
    glow.set_stroke(color=color, width=10, opacity=0.25)
    return glow


def probability_chart(time_frame: ValueTracker) -> VGroup:
    """Two stock-style time histories for probability before/after the barrier.

    The upper panel is linear probability (0--100%).  The lower panel is
    log10(P), with zero at the *top* and -8 at the bottom.  Height and width
    studies change the same two traces; they never create extra colour series.
    """
    start_frame = 8062
    end_frame = 8500
    x_left = -1.78
    x_right = 2.12

    transmission_keys = [
        (8062, 0.0520397455),
        (8259, 0.0520397455),
        (8289, 0.1005647450),
        (8349, 0.0252693046),
        (8390, 0.0520397455),
        (8394, 0.0520397455),
        (8422, 0.3105980378),
        (8472, 0.0115992093),
        (8500, 0.0520397455),
    ]

    def transmission_at(frame: float) -> float:
        if frame <= transmission_keys[0][0]:
            return transmission_keys[0][1]
        for (f0, v0), (f1, v1) in zip(transmission_keys, transmission_keys[1:]):
            if frame <= f1:
                alpha = (frame - f0) / max(1.0, f1 - f0)
                alpha = max(0.0, min(1.0, alpha))
                return v0 + (v1 - v0) * alpha
        return transmission_keys[-1][1]

    def x_for_frame(frame: float) -> float:
        alpha = (frame - start_frame) / (end_frame - start_frame)
        return x_left + max(0.0, min(1.0, alpha)) * (x_right - x_left)

    def make_panel(mode: str, top_y: float, bottom_y: float) -> VGroup:
        static = VGroup()
        y_axis = Line([x_left, bottom_y, 0], [x_left, top_y, 0], color=GREY, stroke_width=1.35)
        x_axis = Line([x_left, bottom_y, 0], [x_right, bottom_y, 0], color=GREY, stroke_width=1.35)
        static.add(y_axis, x_axis)

        if mode == "linear":
            ticks = [(0.0, "0"), (0.5, "50%"), (1.0, "100%")]
            title = MathTex("P", color=WHITE_C, font_size=24).move_to([x_left + 0.15, top_y + 0.24, 0])

            def y_for_probability(value: float) -> float:
                return bottom_y + max(0.0, min(1.0, value)) * (top_y - bottom_y)
        else:
            ticks = [(0.0, "0"), (-2.0, "-2"), (-4.0, "-4"), (-6.0, "-6"), (-8.0, "-8")]
            title = MathTex(r"\log_{10}P", color=WHITE_C, font_size=22).move_to([x_left + 0.34, top_y + 0.24, 0])

            def y_for_probability(value: float) -> float:
                exponent = max(-8.0, min(0.0, math.log10(max(1e-8, value))))
                return top_y - (-exponent / 8.0) * (top_y - bottom_y)

        for value, label_text in ticks:
            if mode == "linear":
                y = bottom_y + value * (top_y - bottom_y)
            else:
                y = top_y - (-value / 8.0) * (top_y - bottom_y)
            static.add(Line([x_left, y, 0], [x_right, y, 0], color=GRID, stroke_width=0.85))
            static.add(text_cn(label_text, 13, GREY).next_to([x_left, y, 0], LEFT, buff=0.06))

        for alpha in (0.25, 0.50, 0.75):
            x = x_left + alpha * (x_right - x_left)
            static.add(Line([x, bottom_y, 0], [x, top_y, 0], color=GRID, stroke_width=0.65, stroke_opacity=0.55))
        static.add(title, MathTex("t", color=GREY, font_size=20).move_to([x_right + 0.14, bottom_y, 0]))

        def trace_group() -> VGroup:
            current = max(start_frame, min(end_frame, time_frame.get_value()))
            sample_count = max(2, int((current - start_frame) / 4.0) + 2)
            frames = [start_frame + (current - start_frame) * i / (sample_count - 1)
                      for i in range(sample_count)]
            front_points = []
            after_points = []
            for frame in frames:
                transmission = transmission_at(frame)
                front = 1.0 - transmission
                x = x_for_frame(frame)
                front_points.append([x, y_for_probability(front), 0])
                after_points.append([x, y_for_probability(transmission), 0])
            front_line = VMobject(color=CYAN, stroke_width=3.0).set_points_as_corners(front_points)
            after_line = VMobject(color=RED, stroke_width=3.0).set_points_as_corners(after_points)
            head_x = x_for_frame(current)
            guide = DashedLine([head_x, bottom_y, 0], [head_x, top_y, 0],
                               color=GREY, stroke_width=0.9, stroke_opacity=0.42,
                               dash_length=0.045)
            front_dot = Dot(front_points[-1], radius=0.042, color=CYAN)
            after_dot = Dot(after_points[-1], radius=0.042, color=RED)
            return VGroup(guide, front_line, after_line, front_dot, after_dot)

        return VGroup(static, always_redraw(trace_group))

    linear_panel = make_panel("linear", 0.62, -0.30)
    log_panel = make_panel("log", -1.22, -3.28)
    legend = VGroup(
        VGroup(Line(LEFT * 0.18, RIGHT * 0.18, color=CYAN, stroke_width=5),
               text_cn("势垒前", 15, CYAN)).arrange(RIGHT, buff=0.07),
        VGroup(Line(LEFT * 0.18, RIGHT * 0.18, color=RED, stroke_width=5),
               text_cn("势垒后", 15, RED)).arrange(RIGHT, buff=0.07),
    ).arrange(RIGHT, buff=0.34).move_to([0.62, 1.03, 0])
    return VGroup(linear_panel, log_panel, legend)


class BlenderRightManimVoiceV1(Scene):
    def setup(self) -> None:
        self.cursor = 0

    def frames_before(self, global_frame: int) -> int:
        return global_frame - GLOBAL_START

    def wait_to(self, global_frame: int) -> None:
        target = self.frames_before(global_frame)
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

        # F05545-F05779: exact hand-off from the preceding square potential.
        barrier = initial_square_potential()
        self.add(barrier)
        target_barrier = barrier.copy().scale(0.86).move_to([-0.22, 0.58, 0])
        self.play_through(5779, Transform(barrier, target_barrier), rate_func=ease_out_cubic)

        # F05780-F05889: V(x), W and V0 are annotations, not chart labels.
        dims = barrier_dimensions(barrier)
        self.play_through(5818, FadeIn(dims[0], shift=LEFT * 0.12), Create(dims[1]))
        self.play_through(5854, GrowArrow(dims[2]), FadeIn(dims[3], shift=UP * 0.08))
        self.play_through(5889, GrowArrow(dims[4]), FadeIn(dims[5], shift=LEFT * 0.08))
        self.play_through(5975, barrier.animate.set_opacity(0.36), dims.animate.set_opacity(0.42))

        # F05976-F06049: the quantum state is introduced by its wavefunction.
        psi = MathTex(r"\psi(\mathbf r,t)", color=WHITE_C, font_size=50).move_to([0, 0.36, 0])
        self.play_through(6049, FadeOut(VGroup(barrier, dims)), Write(psi))

        # F06100-F06160: scale bounce only; keep the original colour and background.
        self.wait_to(6100)
        self.play_through(6160, Indicate(psi, color=WHITE_C, scale_factor=1.12))
        self.wait_to(6168)

        # F06169-F06255: split into real and imaginary components and flash each.
        split = MathTex(
            r"\psi=", r"\operatorname{Re}\psi", r"+i", r"\operatorname{Im}\psi",
            font_size=36,
        ).move_to([0, 0.40, 0])
        split[1].set_color(RED)
        split[3].set_color(BLUE)
        self.play_through(6179, ReplacementTransform(psi, split))
        self.play_through(6204, Indicate(split[1], color=WHITE_C, scale_factor=1.16), rate_func=there_and_back)
        self.wait_to(6225)
        self.play_through(6249, Indicate(split[3], color=WHITE_C, scale_factor=1.16), rate_func=there_and_back)
        self.wait_to(6255)
        self.wait_to(6430)

        density = MathTex(r"|\psi(\mathbf r,t)|^2=\rho(\mathbf r,t)", color=GREEN, font_size=37).move_to([0, -0.72, 0])
        self.play_through(6565, split.animate.shift(UP * 0.48).scale(0.90), Write(density))
        self.play_through(6679, split.animate.set_opacity(0.62), density.animate.set_opacity(0.80))

        # F06680-F06990: region solutions around the barrier.
        bc = VGroup(
            MathTex(r"B e^{i(-kx-\frac{E}{\hbar}t)}", color=RED, font_size=31),
            MathTex(r"C e^{-\kappa x-i\frac{E}{\hbar}t}", color=ORANGE, font_size=31),
            MathTex(r"\kappa=\sqrt{\frac{2m(V_0-E)}{\hbar^2}}", color=GREY, font_size=28),
        ).arrange(DOWN, buff=0.22).move_to([0, 0.20, 0])
        self.play_through(6770, FadeOut(VGroup(split, density)), LaggedStart(*[Write(m) for m in bc], lag_ratio=0.20))
        self.wait_to(6898)
        df = VGroup(
            MathTex(r"D e^{\kappa x-i\frac{E}{\hbar}t}", color=PURPLE, font_size=31),
            MathTex(r"F e^{i(kx-\frac{E}{\hbar}t)}", color=CYAN, font_size=31),
            MathTex(r"k=\sqrt{\frac{2mE}{\hbar^2}}", color=GREY, font_size=28),
        ).arrange(DOWN, buff=0.22).move_to([0, 0.20, 0])
        self.play_through(6990, ReplacementTransform(bc, df))

        # F06991-F08061: formulas stay central; the chart must not appear yet.
        # At F07524 the regional solutions are consolidated into B/C/D/F.
        components = VGroup(
            MathTex(r"B e^{i\left(-kx-\frac{E}{\hbar}t\right)}", color=RED, font_size=27),
            MathTex(r"C e^{-\kappa x-i\frac{E}{\hbar}t}", color=ORANGE, font_size=27),
            MathTex(r"D e^{\kappa x-i\frac{E}{\hbar}t}", color=PURPLE, font_size=27),
            MathTex(r"F e^{i\left(kx-\frac{E}{\hbar}t\right)}", color=CYAN, font_size=27),
        ).arrange(DOWN, buff=0.20).move_to([0, 0.20, 0])
        self.wait_to(7392)
        self.play_through(
            7524,
            FadeOut(df[2]),
            ReplacementTransform(df[0], components[2]),
            ReplacementTransform(df[1], components[3]),
            FadeIn(components[0], shift=RIGHT * 0.10),
            FadeIn(components[1], shift=RIGHT * 0.10),
        )

        self.wait_to(7686)
        self.play_through(
            7837,
            LaggedStart(*[Indicate(m, color=WHITE_C, scale_factor=1.08) for m in components], lag_ratio=0.16),
        )

        exact_t = MathTex(
            r"|F|^2=T=\left[1+\frac{(k^2+\kappa^2)^2\sinh^2(\kappa a)}{4k^2\kappa^2}\right]^{-1}",
            font_size=26,
        ).set_width(4.25).move_to([0, 0.18, 0])
        self.play_through(7935, FadeOut(components), Write(exact_t))

        approx = MathTex(
            r"T\approx", r"\frac{16k^2\kappa^2}{(k^2+\kappa^2)^2}", r"e^{-2\kappa W}",
            font_size=20,
        ).set_width(4.0).move_to([0, 2.3, 0]).scale(0.8).shift(DOWN * (50 * 8 / 1080))
        approx[2].set_color(PURPLE)
        kappa_def = MathTex(r"\kappa=\sqrt{\frac{2m(", r"V_0", r"-E)}{\hbar^2}}",
                            font_size=27).move_to([0, 3.36, 0])
        kappa_def[1].set_color(ORANGE)
        self.play_through(8061, TransformMatchingTex(exact_t, approx), FadeIn(kappa_def, shift=DOWN * 0.08))

        # F08062 onward: two stock-style time histories enter.  The same cyan
        # and red traces carry every subsequent V0/W change.
        chart_time = ValueTracker(8062)
        # Let the chart register on F08062 itself, then finish its entrance
        # smoothly instead of staying fully invisible on the cue frame.
        chart = probability_chart(chart_time).set_opacity(0.20)
        self.add(chart)
        self.wait_to(8062)
        self.play_through(8110, chart.animate.set_opacity(1), chart_time.animate.set_value(8110),
                          rate_func=ease_out_cubic)
        self.play_through(8253, chart_time.animate.set_value(8253),
                          Indicate(approx[2], color=YELLOW, scale_factor=1.08))

        # Height study: 0.8V0 -> 1.3V0 -> V0.
        self.wait_to(8254)
        self.play_through(8289, chart_time.animate.set_value(8289),
                          Indicate(kappa_def[1], color=WHITE_C, scale_factor=1.16))
        self.play_through(8349, chart_time.animate.set_value(8349))
        self.play_through(8390, chart_time.animate.set_value(8390),
                          Indicate(kappa_def[1], color=WHITE_C, scale_factor=1.12))
        self.wait_to(8392)

        # Width study: 0.5W -> 1.5W -> W.
        self.wait_to(8393)
        self.play_through(8422, chart_time.animate.set_value(8422),
                          Indicate(approx[2], color=WHITE_C, scale_factor=1.12))
        self.play_through(8472, chart_time.animate.set_value(8472))
        self.play_through(8500, chart_time.animate.set_value(8500),
                          Indicate(approx[2], color=WHITE_C, scale_factor=1.10))
        self.wait_to(8505)

        # F08506-F08628: chart clears; the governing formula rises.
        formula_group = VGroup(kappa_def, approx)
        self.play_through(8560, FadeOut(chart), formula_group.animate.move_to([0, 2.72, 0]).scale(0.88))
        self.wait_to(8628)

        # F08784-F08984: one measured electron per trial; statistics give T.
        self.wait_to(8784)
        numerator = VGroup(MathTex("Q", color=CYAN, font_size=43), text_cn("隧", 27, CYAN)).arrange(RIGHT, buff=0.03)
        denominator = VGroup(MathTex("Q", color=CYAN, font_size=43), text_cn("总", 27, CYAN)).arrange(RIGHT, buff=0.03)
        fraction_line = Line(LEFT * 0.42, RIGHT * 0.42, color=CYAN, stroke_width=2.5)
        ratio = VGroup(numerator, fraction_line, denominator).arrange(DOWN, buff=0.05).move_to([0, 0.25, 0])
        arrow_t = Arrow(ratio.get_top() + UP * 0.10, approx[0].get_bottom() + DOWN * 0.05,
                        buff=0.08, color=YELLOW, stroke_width=2.6, tip_length=0.14)
        self.play_through(8860, FadeIn(ratio, scale=0.72), GrowArrow(arrow_t))
        self.play_through(
            8984,
            ratio.animate.shift(UP * 0.12).scale(1.07),
            approx[0].animate.shift(UP * 0.07).scale(1.06),
            rate_func=there_and_back,
        )

        # F08985-F09122: the statistical charge flow is the macroscopic current.
        current = MathTex("I", color=ORANGE, font_size=63).move_to([0, -2.35, 0])
        arrow_i = Arrow(current.get_top() + UP * 0.10, ratio.get_bottom() + DOWN * 0.07,
                        buff=0.08, color=ORANGE, stroke_width=2.8, tip_length=0.15)
        self.play_through(9050, FadeIn(current, shift=UP * 0.12), GrowArrow(arrow_i))
        self.play_through(
            GLOBAL_END,
            current.animate.shift(UP * 0.16).scale(1.10),
            ratio.animate.shift(UP * 0.09).scale(1.06),
            rate_func=there_and_back,
        )

        if self.cursor != GLOBAL_END - GLOBAL_START + 1:
            raise RuntimeError(f"Expected 3578 frames, built {self.cursor}")


if __name__ == "__main__":
    print("Render BlenderRightManimVoiceV1 with Manim CE.")
