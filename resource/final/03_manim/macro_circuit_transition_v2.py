"""V2: high-energy Blender zoom-out into a reference-matched Josephson junction.

The shot is intentionally silent and text-light for Resolve assembly.
"""

from pathlib import Path
import numpy as np
from manim import *
from manim.utils.rate_functions import ease_in_out_cubic, ease_out_cubic, ease_out_back

from tunneling_applications_resolve_v8 import make_tunnel_source


ROOT = Path(__file__).resolve().parents[4]
BLENDER_END = ROOT / "renders" / "review_v3_final" / "v3_5399.png"
PEOPLE = ROOT / "remotion_project" / "public" / "assets" / "people"

BG = "#000000"
WHITE_C = "#F4F4F4"
GREY = "#74808D"
DARK = "#07121B"
CYAN = "#58C4DD"
CYAN_LIGHT = "#8AEAFF"
BLUE = "#2459A8"
BLUE_DARK = "#123A70"
ORANGE = "#FF862F"
ORANGE_DARK = "#B94B24"
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
    image = ImageMobject(str(PEOPLE / filename)).set_height(1.22).move_to([4.52, y, 0])
    frame = RoundedRectangle(
        corner_radius=.10, width=1.12, height=1.34,
        fill_color="#0A1119", fill_opacity=1,
        stroke_color=CYAN, stroke_width=1.7,
    ).move_to(image)
    name_label = label(name, 17, WHITE_C, "BOLD", "Courier New").move_to([5.72, y, 0])
    return Group(frame, image, name_label)


def slab(top_points, depth=.25, top=BLUE, side=BLUE_DARK, stroke=CYAN_LIGHT):
    """Create a clean faux-3D parallelogram slab from its top quadrilateral."""
    top_poly = Polygon(*top_points, fill_color=top, fill_opacity=.96, stroke_color=stroke, stroke_width=2.0)
    p0, p1, p2, p3 = [np.array(p) for p in top_points]
    down = np.array([0.0, -depth, 0.0])
    front = Polygon(p0, p1, p1 + down, p0 + down, fill_color=side, fill_opacity=1, stroke_color=stroke, stroke_width=1.3)
    right = Polygon(p1, p2, p2 + down, p1 + down, fill_color=ORANGE_DARK, fill_opacity=.72, stroke_color=stroke, stroke_width=1.0)
    return VGroup(front, right, top_poly)


def josephson_model() -> dict[str, Mobject]:
    """Reference-matched planar Josephson junction over a 2DEG platform."""
    # Shared perspective vector gives all layers the same isometric construction.
    skew = np.array([.92, .66, 0.0])
    x0, x1 = -4.25, 1.10

    base_top = [
        np.array([x0, -1.70, 0]), np.array([x1, -1.70, 0]),
        np.array([x1, -1.70, 0]) + skew, np.array([x0, -1.70, 0]) + skew,
    ]
    base = slab(base_top, depth=.34, top="#55B9C8", side="#B9F0EE", stroke=CYAN_LIGHT)
    base_label = label("2DEG", 22, DARK, "BOLD", "Courier New").move_to([-1.55, -2.18, 0])

    # Orange heterostructure layer between the blue electrodes and 2DEG.
    channel_top = [
        np.array([x0, -1.35, 0]), np.array([x1, -1.35, 0]),
        np.array([x1, -1.35, 0]) + skew, np.array([x0, -1.35, 0]) + skew,
    ]
    channel = slab(channel_top, depth=.20, top="#F0A36C", side="#D97942", stroke=ORANGE)

    # Two superconducting banks with a narrow exposed weak-link gap W1.
    lower_top = [
        np.array([x0, -1.16, 0]), np.array([x1, -1.16, 0]),
        np.array([x1, -.16, 0]) + skew, np.array([x0, -.16, 0]) + skew,
    ]
    upper_top = [
        np.array([x0, .18, 0]) + skew, np.array([x1, .18, 0]) + skew,
        np.array([x1, 1.38, 0]) + skew, np.array([x0, 1.38, 0]) + skew,
    ]
    lower = slab(lower_top, depth=.18, top=BLUE, side=BLUE_DARK)
    upper = slab(upper_top, depth=.18, top="#2E67BC", side=BLUE_DARK)

    gap_left = np.array([-1.95, -.12, 0]) + skew * .55
    gap_right = np.array([-1.95, .22, 0]) + skew * .55
    w_arrow = DoubleArrow(gap_left, gap_right, buff=.02, color=WHITE_C, stroke_width=2.4, tip_length=.12)
    w_label = MathTex(r"W_1", color=WHITE_C, font_size=31).next_to(w_arrow, RIGHT, buff=.10)

    phase_lower = MathTex(r"\Delta e^{-i\phi/2}", color=CYAN_LIGHT, font_size=31).move_to([-1.90, -.92, 0])
    phase_upper = MathTex(r"\Delta e^{i\phi/2}", color=CYAN_LIGHT, font_size=31).move_to([.05, 1.96, 0])

    electron_l = Dot([-2.58, .06, 0], radius=.095, color=RED)
    electron_r = Dot([-.78, .06, 0], radius=.095, color=RED)
    for dot in (electron_l, electron_r):
        dot.add(Dot(dot.get_center(), radius=.20, color=RED, fill_opacity=.12, stroke_width=0))
    tunnel_arrow = Arrow(electron_l.get_center(), electron_r.get_center(), buff=.16, color=RED, stroke_width=3.0, tip_length=.17)
    tunnel_symbol = MathTex(r"\tilde{R}", color=RED, font_size=30).next_to(tunnel_arrow, UP, buff=.07)

    # Small phase diagram, copied structurally from the supplied reference.
    inset_box = RoundedRectangle(corner_radius=.05, width=2.45, height=1.48, fill_color="#07121B", fill_opacity=.94, stroke_color=GREY, stroke_width=1.3).move_to([-4.20, 2.52, 0])
    ix0, iy0 = -5.22, 2.08
    ix1, iy1 = -3.24, 2.98
    ax_x = Arrow([ix0, iy0, 0], [ix1, iy0, 0], buff=0, color=GREY, stroke_width=1.2, tip_length=.09)
    ax_y = Arrow([ix0, iy0, 0], [ix0, iy1, 0], buff=0, color=GREY, stroke_width=1.2, tip_length=.09)
    diamond = Polygon(
        [ix0 + .45, iy0, 0], [ix0 + .92, iy0 + .72, 0],
        [ix0 + 1.39, iy0, 0], [ix0 + .92, iy0 - .02, 0],
        fill_color=CYAN, fill_opacity=.14, stroke_color=CYAN_LIGHT, stroke_width=1.4,
    )
    topo = label("Topological", 12, CYAN_LIGHT, "BOLD", "Courier New").move_to([ix0 + .91, iy0 + .31, 0])
    trivial = label("Trivial", 12, WHITE_C, "BOLD", "Courier New").move_to([ix0 + 1.48, iy0 + .68, 0])
    inset = VGroup(inset_box, ax_x, ax_y, diamond, topo, trivial)

    model = VGroup(base, channel, lower, upper, base_label, phase_lower, phase_upper,
                   w_arrow, w_label, electron_l, electron_r, tunnel_arrow, tunnel_symbol, inset)
    model.move_to([-1.15, -.05, 0]).scale(.92)
    weak_link = VGroup(w_arrow, w_label, electron_l, electron_r, tunnel_arrow, tunnel_symbol)
    return {"all": model, "weak_link": weak_link, "electrons": VGroup(electron_l, electron_r), "arrow": tunnel_arrow}


def radial_speed_lines(target: np.ndarray, count=30) -> VGroup:
    """Long converging streaks that make the outgoing zoom read as violent scale change."""
    lines = VGroup()
    for i in range(count):
        angle = TAU * i / count + .035 * np.sin(i * 2.7)
        outer = 7.2 if i % 3 else 8.1
        inner = 1.05 + .24 * (i % 4)
        p0 = target + np.array([np.cos(angle) * outer, np.sin(angle) * outer * .58, 0])
        p1 = target + np.array([np.cos(angle) * inner, np.sin(angle) * inner * .58, 0])
        line = Line(p0, p1, color=CYAN_LIGHT if i % 4 else WHITE_C,
                    stroke_width=2.0 if i % 3 else 3.4, stroke_opacity=.68)
        lines.add(line)
    return lines


def perspective_speed_lines(target: np.ndarray, reveal: float, rotation: float, opacity: float, count=28) -> VGroup:
    """Tapered semi-transparent streaks sharing one vanishing point.

    ``reveal`` grows the streaks rapidly from the outer frame toward the
    vanishing point.  Wider outer bases and narrow inner tips preserve the
    intended perspective instead of reading as a flat starburst.
    """
    streaks = VGroup()
    progress = np.clip(reveal, 0.001, 1.0)
    for i in range(count):
        angle = TAU * i / count + .028 * np.sin(i * 2.7) + rotation
        outer_radius = 7.7 if i % 3 else 8.45
        inner_radius = .72 + .16 * (i % 4)
        direction = np.array([np.cos(angle), .60 * np.sin(angle), 0.0])
        p_outer = target + direction * outer_radius
        p_inner = target + direction * inner_radius
        p_tip = interpolate(p_outer, p_inner, progress)
        tangent = p_inner - p_outer
        tangent /= max(np.linalg.norm(tangent), 1e-6)
        normal = np.array([-tangent[1], tangent[0], 0.0])
        outer_half_width = .018 if i % 3 else .031
        tip_half_width = outer_half_width * .10
        streak = Polygon(
            p_outer + normal * outer_half_width,
            p_outer - normal * outer_half_width,
            p_tip - normal * tip_half_width,
            p_tip + normal * tip_half_width,
            fill_color=CYAN_LIGHT if i % 4 else WHITE_C,
            fill_opacity=opacity * (.82 if i % 3 else 1.0),
            stroke_width=0,
        )
        streaks.add(streak)
    return streaks


class MacroCircuitTransitionV2(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        blender = ImageMobject(str(BLENDER_END)).set_width(config.frame_width)
        self.add(blender)
        self.wait(.20)

        target = np.array([-1.05, -.08, 0])
        line_reveal = ValueTracker(0.0)
        line_rotation = ValueTracker(0.0)
        line_opacity = ValueTracker(.34)
        speed_lines = always_redraw(
            lambda: perspective_speed_lines(
                target,
                line_reveal.get_value(),
                line_rotation.get_value(),
                line_opacity.get_value(),
            )
        )

        josephson = josephson_model()
        model = josephson["all"]
        model.save_state()
        model.scale(3.35).set_opacity(0.0)
        self.add(model, speed_lines)

        # Motion streaks begin first. Exactly three 60-fps frames later the
        # oversized transparent junction begins converging to its final size.
        self.play(
            blender.animate(run_time=1.28, rate_func=ease_in_out_cubic).scale(.045).move_to(target).set_opacity(.05),
            line_reveal.animate(run_time=.44, rate_func=ease_out_cubic).set_value(1.0),
            line_rotation.animate(run_time=1.28, rate_func=ease_in_out_cubic).set_value(-5 * DEGREES),
            Succession(
                Wait(3 / 60),
                Restore(model, run_time=1.05, rate_func=ease_out_cubic),
            ),
        )
        self.play(
            blender.animate.set_opacity(0),
            line_opacity.animate.set_value(0),
            run_time=.18,
            rate_func=ease_out_cubic,
        )
        speed_lines.clear_updaters()
        self.remove(blender, speed_lines)

        # Short overshoot after the large transparent convergence.
        self.play(model.animate.scale(1.035), run_time=.15, rate_func=ease_out_back)
        self.play(model.animate.scale(1 / 1.035), run_time=.18, rate_func=ease_out_cubic)

        portraits = Group(
            portrait_card("john_clarke_2025_official.jpg", "JOHN CLARKE", 1.48),
            portrait_card("michel_devoret_2025_official.jpg", "MICHEL DEVORET", -.02),
            portrait_card("john_martinis_2025_official.jpg", "JOHN MARTINIS", -1.52),
        )
        nobel = label("2025 诺贝尔物理学奖", 27, YELLOW, "BOLD").move_to([4.72, 3.15, 0])
        portraits.set_opacity(0)
        nobel.set_opacity(0)
        self.add(portraits, nobel)
        self.play(portraits.animate.set_opacity(1), nobel.animate.set_opacity(1), run_time=.55)

        # Make tunnelling visible without turning the sequence into a labelled slide.
        pulse = Dot(josephson["arrow"].get_start(), radius=.10, color=WHITE_C)
        pulse_glow = Dot(pulse.get_center(), radius=.25, color=RED, fill_opacity=.18, stroke_width=0)
        pulse_group = VGroup(pulse_glow, pulse)
        self.add(pulse_group)
        path = Line(josephson["arrow"].get_start(), josephson["arrow"].get_end())
        self.play(MoveAlongPath(pulse_group, path), Indicate(josephson["weak_link"], color=YELLOW, scale_factor=1.10), run_time=1.10, rate_func=ease_in_out_cubic)
        self.play(FadeOut(pulse_group), run_time=.18)
        self.wait(.38)

        # Dive into the weak link and morph into the established 2D tunnelling diagram.
        focus_ring = Circle(radius=.62, color=YELLOW, stroke_width=3.4).move_to(josephson["weak_link"].get_center())
        self.play(Create(focus_ring), model.animate.set_opacity(.38), portraits.animate.set_opacity(.32), nobel.animate.set_opacity(.32), run_time=.42)
        projection_final = make_tunnel_source().scale(.86).move_to(LEFT * .68)
        projection = projection_final.copy().scale(.050).move_to(josephson["weak_link"].get_center()).set_opacity(.08)
        self.add(projection)
        exit_lines = radial_speed_lines(josephson["weak_link"].get_center(), count=22).set_color(YELLOW)
        self.play(
            Transform(projection, projection_final),
            FadeOut(Group(model, portraits, nobel, focus_ring)),
            LaggedStart(*[ShowPassingFlash(line, time_width=.40) for line in exit_lines], lag_ratio=.010),
            run_time=1.62,
            rate_func=ease_in_out_cubic,
        )
        projection.become(projection_final)
        self.wait(.75)


if __name__ == "__main__":
    print("Render MacroCircuitTransitionV2 with the Manim CLI.")
