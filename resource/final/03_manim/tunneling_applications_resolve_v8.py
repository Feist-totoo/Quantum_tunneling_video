"""Intermediate directed layout with the original V5 final relationship map.

Only the current central demonstration animates. A dark spotlight scrim
reduces the brightness and opacity of every background object while the active
demonstration stays crisp. Finished demonstrations freeze into the directed
intermediate regions, then recompose into the original V5 final relationship map.
"""

from __future__ import annotations

from pathlib import Path
import math

import numpy as np

from manim import *
from manim.utils.color import ManimColor
from manim.utils.rate_functions import ease_in_out_cubic


ROOT = Path(__file__).resolve().parents[3]
BLENDER_END = ROOT / "renders" / "review_v3_final" / "v3_5399.png"

BG = "#000000"
WHITE_C = "#F4F4F4"
GREY = "#64748B"
GREY_DARK = "#17212C"
CYAN = "#58C4DD"
CYAN_LIGHT = "#8AEAFF"
BLUE = "#4A8DFF"
BLUE_DIM = "#1E3A5F"
GREEN = "#5CD0B3"
ORANGE = "#FF862F"
RED = "#FC6255"
YELLOW = "#FFFF00"
PURPLE = "#9A72AC"
FONT = "Noto Sans SC"

STAGE_SHIFT = LEFT * 0.60 + DOWN * 0.03
# Intermediate positions come from the 1920 x 1080 directive canvas.
# These guides are not rendered. The final constants remain exactly V5.
TUNNEL_DOCK = np.array([-4.572, 2.452, 0.0])
APP_DOCKS = (
    np.array([-4.324, -1.048, 0.0]),
    np.array([-0.036, -1.044, 0.0]),
    np.array([4.814, -1.152, 0.0]),
)
INTERMEDIATE_APP_SCALES = (0.350, 0.340, 0.310)
FINAL_TUNNEL = np.array([0.00, 2.30, 0.0])
FINAL_APPS = (
    np.array([-4.25, -1.55, 0.0]),
    np.array([0.00, -1.55, 0.0]),
    np.array([4.25, -1.55, 0.0]),
)
V5_FINAL_APP_SCALE = 0.220 * 1.180
FINAL_APP_SCALE_FACTORS = tuple(V5_FINAL_APP_SCALE / scale for scale in INTERMEDIATE_APP_SCALES)

config.background_color = BG
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 60


def txt(text: str, size: int = 22, color: str = WHITE_C, font: str = FONT, weight: str = "NORMAL") -> Text:
    return Text(text, font=font, font_size=size, color=color, weight=weight)


def rect(width: float, height: float, fill: str, opacity: float, stroke: str, stroke_width: float, pos) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        fill_color=fill,
        fill_opacity=opacity,
        stroke_color=stroke,
        stroke_width=stroke_width,
    ).move_to(pos)


def wave(x0: float, x1: float, y0: float, amp: float, freq: float, color: str, decay: float = 0.0) -> VMobject:
    xs = np.linspace(x0, x1, 220)
    env = np.exp(-decay * np.maximum(xs - x0, 0.0)) if decay else np.ones_like(xs)
    ys = y0 + amp * env * np.sin(freq * (xs - x0))
    mob = VMobject(color=color, stroke_width=2.6)
    mob.set_points_smoothly(np.column_stack((xs, ys, np.zeros_like(xs))))
    return mob


def clear_all_updaters(mob: Mobject) -> None:
    mob.clear_updaters()
    for submob in mob.submobjects:
        clear_all_updaters(submob)


def make_tunnel_source() -> VGroup:
    y = -0.18
    barrier = rect(0.72, 3.25, CYAN, 0.25, CYAN, 2.0, [-0.05, 0.08, 0])
    base = Arrow([-3.05, y, 0], [3.08, y, 0], buff=0, color=GREY, stroke_width=1.5, tip_length=0.16)
    energy = DashedLine([-2.75, 0.64, 0], [2.83, 0.64, 0], color=YELLOW, stroke_width=1.6, dash_length=0.12)
    incident = wave(-2.90, -0.48, y, 0.34, 9.5, CYAN)
    inside = wave(-0.42, 0.31, y, 0.29, 9.5, GREEN, decay=2.4)
    transmitted = wave(0.37, 2.78, y, 0.12, 9.5, GREEN)
    title = txt("量子隧穿", 34, CYAN, weight="BOLD").move_to([-0.32, 2.15, 0])
    v0 = txt("V0", 21, ORANGE, font="Courier New", weight="BOLD").next_to(barrier, UP, buff=0.12)
    e_label = txt("E < V0", 19, YELLOW, font="Courier New").move_to([-2.28, 0.92, 0])
    width_brace = Brace(barrier, DOWN, color=PURPLE, sharpness=0.7)
    width_label = txt("W", 18, PURPLE, font="Courier New", weight="BOLD").next_to(width_brace, DOWN, buff=0.03)
    return VGroup(base, barrier, energy, incident, inside, transmitted, title, v0, e_label, width_brace, width_label)


def make_source_arrow(color: str) -> VGroup:
    start = np.array([-4.55, 2.25, 0.0])
    end = np.array([-3.56, 1.26, 0.0])
    arrow = CurvedArrow(start, end, angle=-0.34, color=color, stroke_width=2.8, tip_length=0.16)
    pulse = Dot(start, radius=0.055, color=color)
    return VGroup(arrow, pulse)


def make_nand() -> dict[str, Mobject]:
    title = txt("NAND 闪存 — 隧穿擦写", 42, ORANGE, weight="BOLD").to_edge(UP, buff=0.42)
    cg = rect(3.40, 0.70, "#1E40AF", 0.90, BLUE, 2, [-3.25, 1.52, 0])
    fg = rect(3.40, 0.90, "#134E4A", 0.90, CYAN, 2, [-3.25, 0.24, 0])
    oxide = rect(3.40, 0.55, "#7C2D12", 0.64, ORANGE, 2, [-3.25, -0.48, 0])
    substrate = rect(3.40, 1.10, "#1E293B", 0.93, GREY, 2, [-3.25, -1.32, 0])
    labels = VGroup(
        txt("控制栅 CG (+HV)", 19, BLUE).move_to(cg),
        txt("浮栅 FG", 19, CYAN).move_to(fg),
        txt("SiO₂  ~10 nm", 17, ORANGE).move_to(oxide),
        txt("Si 衬底", 19, GREY).move_to(substrate),
    )
    cell = VGroup(cg, fg, oxide, substrate, labels)

    data_title = txt("存储单元数据", 24, WHITE_C, weight="BOLD").move_to([2.80, 1.95, 0])
    bits = VGroup(*[
        txt(value, 27, GREEN, font="Courier New")
        for value in ("10110101", "01001110", "11100011", "00101101")
    ]).arrange(DOWN, buff=0.18).move_to([2.80, 0.53, 0])
    state = txt("状态: 已写入", 22, GREEN).move_to([2.80, -0.82, 0])
    charge = txt("浮栅电荷: ●●●●●", 22, CYAN).move_to([2.80, -1.30, 0])
    data = VGroup(data_title, bits, state, charge)

    hv_arrow = Arrow(cg.get_top(), cg.get_top() + UP * 0.56, buff=0, color=YELLOW, stroke_width=3.0, tip_length=0.18)
    hv_label = txt("高压 ~20V", 20, YELLOW).next_to(hv_arrow, UP, buff=0.04)
    hv = VGroup(hv_arrow, hv_label)
    all_mob = VGroup(title, cell, data, hv).shift(STAGE_SHIFT)
    return {
        "all": all_mob,
        "title": title,
        "cell": cell,
        "fg": fg,
        "oxide": oxide,
        "data": data,
        "bits": bits,
        "state": state,
        "charge": charge,
        "hv": hv,
    }


def make_stm() -> dict[str, Mobject]:
    title = txt("扫描隧道显微镜 (STM)", 42, CYAN, weight="BOLD").to_edge(UP, buff=0.42)
    tip_body = Polygon(
        [-3.90, 2.02, 0], [-0.90, 2.02, 0], [-2.40, 0.10, 0],
        fill_color="#475569", fill_opacity=0.88, stroke_color="#94A3B8", stroke_width=2,
    )
    tip_apex = Dot([-2.40, 0.10, 0], radius=0.08, color=WHITE_C)
    tip_label = txt("W 探针尖端 (单原子级)", 20, WHITE_C).move_to([-2.40, 2.42, 0])
    gap_line = DashedLine([-2.40, 0.10, 0], [-2.40, -0.53, 0], color=YELLOW, stroke_width=2.0)
    gap_label = txt("d ≈ 1 nm", 18, YELLOW).next_to(gap_line, RIGHT, buff=0.10)

    xs = np.linspace(-4.75, 0.05, 360)
    ys = -0.53 + 0.12 * np.sin(4 * np.pi * xs)
    surface = VMobject(color=BLUE, stroke_width=2.8)
    surface.set_points_smoothly(np.column_stack((xs, ys, np.zeros_like(xs))))
    surface_fill = Rectangle(width=4.80, height=1.18, fill_color="#1E293B", fill_opacity=0.92, stroke_width=0).move_to([-2.35, -1.12, 0])
    surface_label = txt("样品表面（原子级分辨）", 20, BLUE).move_to([-2.35, -1.70, 0])

    def make_arc(x_value: float, tip_y: float) -> VMobject:
        surface_y = -0.53 + 0.12 * math.sin(4 * math.pi * x_value)
        ys_arc = np.linspace(tip_y - 0.04, surface_y + 0.04, 12)
        xs_arc = x_value + 0.045 * np.sin(np.arange(12) * 1.8)
        arc = VMobject(color=YELLOW, stroke_width=3.0)
        arc.set_points_smoothly(np.column_stack((xs_arc, ys_arc, np.zeros_like(xs_arc))))
        return arc

    current_arc = make_arc(-2.40, 0.10)
    tip_group = VGroup(tip_body, tip_apex, tip_label, gap_line, gap_label, current_arc)
    sample_group = VGroup(surface_fill, surface, surface_label)

    bar_x = 3.72
    bar_bottom = -1.90
    bar_max_h = 3.60
    bar_width = 1.08
    axis = Arrow([bar_x, bar_bottom, 0], [bar_x, bar_bottom + bar_max_h + 0.34, 0], color=WHITE_C, stroke_width=2.1, tip_length=0.18)
    axis_label = txt("I (nA)", 22, WHITE_C, font="Courier New").next_to(axis.get_top(), RIGHT, buff=0.14)
    ticks = VGroup()
    for value in (0.00, 0.25, 0.50, 0.75, 1.00):
        ty = bar_bottom + value * bar_max_h
        tick = Line([bar_x - 0.10, ty, 0], [bar_x + 0.10, ty, 0], color=WHITE_C, stroke_width=1.4)
        tick_label = txt(f"{value:.2f}", 15, GREY, font="Courier New").next_to(tick, LEFT, buff=0.08)
        ticks.add(tick, tick_label)
    initial_i = math.exp(-1.1)
    initial_h = initial_i * bar_max_h
    bar = Rectangle(width=bar_width, height=initial_h, fill_color=GREEN, fill_opacity=0.88, stroke_color=GREEN, stroke_width=2).move_to([bar_x, bar_bottom + initial_h / 2, 0])
    value_text = txt(f"I = {initial_i:.3f} nA", 25, YELLOW, font="Courier New").move_to([bar_x, bar_bottom + bar_max_h + 0.80, 0])
    bar_title = txt("隧道电流", 24, CYAN, weight="BOLD").move_to([bar_x, bar_bottom + bar_max_h + 1.24, 0])
    meter = VGroup(axis, axis_label, ticks, bar, value_text, bar_title)
    all_mob = VGroup(title, tip_group, sample_group, meter).shift(STAGE_SHIFT)
    return {
        "all": all_mob,
        "title": title,
        "tip_group": tip_group,
        "sample": sample_group,
        "tip_body": tip_body,
        "tip_apex": tip_apex,
        "tip_label": tip_label,
        "gap_line": gap_line,
        "gap_label": gap_label,
        "arc": current_arc,
        "bar": bar,
        "value": value_text,
        "meter": meter,
        "bar_x": bar_x + STAGE_SHIFT[0],
        "bar_bottom": bar_bottom + STAGE_SHIFT[1],
        "bar_max_h": bar_max_h,
        "bar_width": bar_width,
    }


def make_cmos() -> dict[str, Mobject]:
    title = txt("CMOS 芯片 — 量子隧穿漏电发热", 39, RED, weight="BOLD").to_edge(UP, buff=0.42)
    vdd = Line([-5.20, 2.34, 0], [1.72, 2.34, 0], color=RED, stroke_width=2.5)
    gnd = Line([-5.20, -2.32, 0], [1.72, -2.32, 0], color=GREY, stroke_width=2.5)
    vdd_label = txt("VDD", 21, RED, font="Courier New").next_to(vdd, LEFT, buff=0.10)
    gnd_label = txt("GND", 21, GREY, font="Courier New").next_to(gnd, LEFT, buff=0.10)

    p_body = rect(1.20, 1.20, "#1D3D7A", 0.88, BLUE, 2, [-2.60, 0.96, 0])
    p_oxide = rect(0.18, 1.20, ORANGE, 0.88, ORANGE, 1.5, ORIGIN).next_to(p_body, LEFT, buff=0)
    p_gate = rect(0.70, 1.20, BLUE_DIM, 0.92, BLUE, 2, ORIGIN).next_to(p_oxide, LEFT, buff=0)
    p_source = Line(p_body.get_top(), p_body.get_top() + UP * 1.18, color=RED, stroke_width=2.5)
    p_drain = Line(p_body.get_bottom(), p_body.get_bottom() + DOWN * 0.46, color=BLUE, stroke_width=2.5)
    p_label = txt("PMOS", 18, BLUE, font="Courier New").next_to(p_body, RIGHT, buff=0.15)

    n_body = rect(1.20, 1.20, "#0F3830", 0.88, CYAN, 2, [-2.60, -0.96, 0])
    n_oxide = rect(0.18, 1.20, ORANGE, 0.88, ORANGE, 1.5, ORIGIN).next_to(n_body, LEFT, buff=0)
    n_gate = rect(0.70, 1.20, BLUE_DIM, 0.92, BLUE, 2, ORIGIN).next_to(n_oxide, LEFT, buff=0)
    n_drain = Line(n_body.get_top(), n_body.get_top() + UP * 0.46, color=BLUE, stroke_width=2.5)
    n_source = Line(n_body.get_bottom(), n_body.get_bottom() + DOWN * 1.18, color=GREY, stroke_width=2.5)
    n_label = txt("NMOS", 18, CYAN, font="Courier New").next_to(n_body, RIGHT, buff=0.15)

    mid = Line([-2.60, -0.50, 0], [-2.60, 0.50, 0], color=BLUE, stroke_width=2.5)
    out_wire = Line([-2.60, 0.0, 0], [-0.80, 0.0, 0], color=YELLOW, stroke_width=2.5)
    out_dot = Dot([-2.60, 0.0, 0], radius=0.10, color=YELLOW)
    out_label = txt("V_out", 22, YELLOW, font="Courier New").move_to([-0.24, 0.0, 0])
    p_input = Line(p_gate.get_left(), p_gate.get_left() + LEFT * 0.50, color=YELLOW, stroke_width=2.0)
    n_input = Line(n_gate.get_left(), n_gate.get_left() + LEFT * 0.50, color=YELLOW, stroke_width=2.0)
    input_join = Line(p_input.get_end(), n_input.get_end(), color=YELLOW, stroke_width=2.0)
    input_label = txt("V_in", 22, YELLOW, font="Courier New").next_to(input_join, LEFT, buff=0.13)
    p_oxide_label = txt("d_ox = 1.2 nm", 15, ORANGE).move_to(p_oxide.get_center() + LEFT * 0.34 + UP * 0.70)
    n_oxide_label = txt("d_ox = 1.2 nm", 15, ORANGE).move_to(n_oxide.get_center() + LEFT * 0.34 + DOWN * 0.70)
    transistor = VGroup(
        p_body, p_oxide, p_gate, p_source, p_drain, p_label,
        n_body, n_oxide, n_gate, n_drain, n_source, n_label,
        mid, out_wire, out_dot, out_label, p_input, n_input, input_join, input_label,
        p_oxide_label, n_oxide_label,
    )

    gauge_center = np.array([3.75, 0.16, 0])
    gauge_radius = 1.40

    def gauge_arc(fraction: float, color: str, width: float = 14) -> Arc:
        return Arc(radius=gauge_radius, start_angle=PI, angle=-max(0.01, fraction * PI), arc_center=gauge_center, color=color, stroke_width=width)

    gauge_bg = gauge_arc(1.0, GREY)
    gauge_fill = gauge_arc(0.01, RED)
    gauge_title = txt("漏电功耗", 26, RED, weight="BOLD").move_to([3.75, 2.10, 0])

    def stats_group(node: float, temp: float, power: float) -> VGroup:
        return VGroup(
            txt(f"T_j = {temp:.0f} degC", 22, RED, font="Courier New"),
            txt(f"P_leak = {power:.1f} W", 22, ORANGE, font="Courier New"),
            txt(f"L_gate = {node:.0f} nm", 22, CYAN, font="Courier New"),
            txt("I_leak ~ exp(-2*k*d_ox)", 20, PURPLE, font="Courier New"),
        ).arrange(DOWN, buff=0.13, aligned_edge=LEFT).move_to([3.75, -1.13, 0])

    stats = stats_group(5, 42, 0)
    gauge = VGroup(gauge_bg, gauge_fill, gauge_title, stats)
    all_mob = VGroup(title, vdd, gnd, vdd_label, gnd_label, transistor, gauge).shift(STAGE_SHIFT)
    return {
        "all": all_mob,
        "title": title,
        "rails": VGroup(vdd, gnd, vdd_label, gnd_label),
        "transistor": transistor,
        "p_oxide": p_oxide,
        "n_oxide": n_oxide,
        "gauge": gauge,
        "gauge_fill": gauge_fill,
        "stats": stats,
        "gauge_center": gauge_center + STAGE_SHIFT,
        "gauge_radius": gauge_radius,
        "stats_group": stats_group,
    }


class TunnellingApplicationsResolveV8(Scene):
    def freeze_and_dock(self, mob: Mobject, target: np.ndarray, scale: float = 0.220) -> None:
        clear_all_updaters(mob)
        mob.set_z_index(22)
        self.play(
            mob.animate.scale(scale).move_to(target).set_opacity(0.62),
            run_time=0.86,
            rate_func=ease_in_out_cubic,
        )
        clear_all_updaters(mob)
        mob.set_z_index(2)
        mob.suspend_updating(recursive=True)

    def construct(self) -> None:
        self.camera.background_color = BG

        # The preceding macro-circuit clip ends on this exact full-size 2D
        # tunnelling diagram.  Begin with the same geometry so Resolve can use
        # a direct cut without a duplicate Blender-to-diagram transition.
        projection = make_tunnel_source().scale(0.86).move_to(LEFT * 0.68)
        self.add(projection)
        self.wait(0.18)
        self.play(projection.animate.scale(0.645).move_to(TUNNEL_DOCK).set_opacity(0.30), run_time=0.82, rate_func=ease_in_out_cubic)
        clear_all_updaters(projection)
        projection.suspend_updating(recursive=True)

        self.play_nand(projection)
        self.play_stm(projection)
        self.play_cmos(projection)

        # Hold the directed intermediate layout long enough to read it.
        self.play(
            projection.animate.set_opacity(0.70),
            *[mob.animate.set_opacity(0.78) for mob in self.docked],
            run_time=0.35,
            rate_func=ease_in_out_cubic,
        )
        self.wait(0.20)

        # Restore the original V5 final hierarchy, scale, and arrow geometry.
        self.play(
            projection.animate.scale(0.853).move_to(FINAL_TUNNEL).set_opacity(0.92),
            *[
                mob.animate.scale(scale_factor).move_to(target).set_opacity(0.88)
                for mob, target, scale_factor in zip(self.docked, FINAL_APPS, FINAL_APP_SCALE_FACTORS)
            ],
            run_time=1.35,
            rate_func=ease_in_out_cubic,
        )
        arrows = VGroup(
            CurvedArrow(projection.get_bottom() + LEFT * 0.34, self.docked[0].get_top() + UP * 0.04, angle=-0.30, color=ORANGE, stroke_width=3.2, tip_length=0.18),
            Arrow(projection.get_bottom(), self.docked[1].get_top() + UP * 0.04, buff=0.08, color=CYAN, stroke_width=3.2, tip_length=0.18),
            CurvedArrow(projection.get_bottom() + RIGHT * 0.34, self.docked[2].get_top() + UP * 0.04, angle=0.30, color=RED, stroke_width=3.2, tip_length=0.18),
        ).set_z_index(30)
        self.play(LaggedStart(*[Create(arrow) for arrow in arrows], lag_ratio=0.16), run_time=1.85)
        self.wait(0.60)

    @property
    def docked(self) -> list[Mobject]:
        if not hasattr(self, "_docked"):
            self._docked = []
        return self._docked

    def begin_application(self, color: str) -> tuple[VGroup, Rectangle]:
        # The scrim behaves like a spotlight mask: everything already present
        # loses brightness while the active demonstration is placed above it.
        scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=BG,
            fill_opacity=0.0,
            stroke_width=0,
        ).set_z_index(10)
        arrow = make_source_arrow(color).set_z_index(24)
        self.add(scrim)
        self.play(
            scrim.animate.set_fill(opacity=0.76),
            Create(arrow[0]),
            FadeIn(arrow[1], scale=0.5),
            run_time=0.48,
            rate_func=ease_in_out_cubic,
        )
        return arrow, scrim

    def play_nand(self, tunnel: Mobject) -> None:
        arrow, scrim = self.begin_application(ORANGE)
        demo = make_nand()
        demo["all"].set_z_index(22)
        self.play(FadeIn(demo["title"], shift=UP * 0.12), FadeIn(demo["cell"]), FadeIn(demo["data"]), run_time=0.58)
        self.play(GrowArrow(demo["hv"][0]), FadeIn(demo["hv"][1]), run_time=0.28)

        x_positions = np.linspace(demo["oxide"].get_left()[0] + 0.30, demo["oxide"].get_right()[0] - 0.30, 9)
        electrons = VGroup(*[Dot([x, demo["oxide"].get_bottom()[1] - 0.36, 0], radius=0.075, color=CYAN_LIGHT) for x in x_positions])
        self.add(electrons)
        self.play(LaggedStart(*[dot.animate.move_to([dot.get_x(), demo["fg"].get_center()[1], 0]) for dot in electrons], lag_ratio=0.08), run_time=0.86, rate_func=rush_into)
        self.play(FadeOut(electrons), demo["fg"].animate.set_fill("#0E7490", opacity=0.95), run_time=0.20)

        erased_bits = VGroup(*[txt("11111111", 27, ORANGE, font="Courier New") for _ in range(4)]).arrange(DOWN, buff=0.18).move_to(demo["bits"])
        erased_state = txt("状态: 已擦除 (FF)", 22, ORANGE).move_to(demo["state"])
        erased_charge = txt("浮栅电荷: ○○○○○", 22, GREY).move_to(demo["charge"])
        self.play(Transform(demo["bits"], erased_bits), Transform(demo["state"], erased_state), Transform(demo["charge"], erased_charge), run_time=0.52)

        write_xs = np.linspace(demo["oxide"].get_left()[0] + 0.48, demo["oxide"].get_right()[0] - 0.48, 6)
        write_electrons = VGroup(*[Dot([x, demo["oxide"].get_bottom()[1] - 0.34, 0], radius=0.075, color=CYAN_LIGHT) for x in write_xs])
        self.add(write_electrons)
        self.play(LaggedStart(*[dot.animate.move_to([dot.get_x(), demo["fg"].get_center()[1], 0]) for dot in write_electrons], lag_ratio=0.10), run_time=0.62, rate_func=rush_into)
        programmed_bits = VGroup(*[
            txt(value, 27, GREEN, font="Courier New")
            for value in ("00110111", "10101010", "01110001", "11001100")
        ]).arrange(DOWN, buff=0.18).move_to(demo["bits"])
        programmed_state = txt("状态: 写入数据", 22, GREEN).move_to(demo["state"])
        programmed_charge = txt("浮栅电荷: ●●○●○", 22, CYAN).move_to(demo["charge"])
        self.play(
            FadeOut(write_electrons),
            Transform(demo["bits"], programmed_bits),
            Transform(demo["state"], programmed_state),
            Transform(demo["charge"], programmed_charge),
            run_time=0.54,
        )
        self.wait(0.16)
        self.play(FadeOut(arrow), run_time=0.18)
        self.freeze_and_dock(demo["all"], APP_DOCKS[0], INTERMEDIATE_APP_SCALES[0])
        self.docked.append(demo["all"])
        self.play(FadeOut(scrim), run_time=0.34)
        self.remove(scrim)

    def play_stm(self, tunnel: Mobject) -> None:
        arrow, scrim = self.begin_application(CYAN)
        demo = make_stm()
        demo["all"].set_z_index(22)
        self.play(FadeIn(demo["title"], shift=UP * 0.12), FadeIn(demo["sample"]), FadeIn(demo["tip_group"]), FadeIn(demo["meter"]), run_time=0.58)

        scan_positions = np.concatenate((np.linspace(-3.42, -1.06, 7), np.linspace(-1.06, -3.12, 6))) + STAGE_SHIFT[0]
        current_x = demo["tip_apex"].get_x()
        for new_x in scan_positions:
            dx = float(new_x - current_x)
            surface_y = -0.53 + STAGE_SHIFT[1] + 0.12 * math.sin(4 * math.pi * (new_x - STAGE_SHIFT[0]))
            tip_y = surface_y + 0.63
            gap_d = max(0.15, abs(surface_y - (-0.53 + STAGE_SHIFT[1])) * 9 + 0.80)
            current_i = math.exp(-1.1 * min(9.8, gap_d))
            current_h = max(0.03, current_i * demo["bar_max_h"])

            new_tip_body = demo["tip_body"].copy().shift([dx, tip_y - demo["tip_apex"].get_y(), 0])
            new_tip_apex = demo["tip_apex"].copy().move_to([new_x, tip_y, 0])
            new_tip_label = demo["tip_label"].copy().shift([dx, tip_y - demo["tip_apex"].get_y(), 0])
            new_gap_line = DashedLine([new_x, tip_y, 0], [new_x, surface_y, 0], color=YELLOW, stroke_width=2.0)
            new_gap_label = txt("d ≈ 1 nm", 18, YELLOW).next_to(new_gap_line, RIGHT, buff=0.10)
            ys_arc = np.linspace(tip_y - 0.04, surface_y + 0.04, 12)
            xs_arc = new_x + 0.045 * np.sin(np.arange(12) * 1.8)
            new_arc = VMobject(color=YELLOW, stroke_width=3.0).set_points_smoothly(np.column_stack((xs_arc, ys_arc, np.zeros_like(xs_arc))))

            bar_color = interpolate_color(ManimColor(BLUE_DIM), ManimColor(GREEN), min(1.0, current_i))
            new_bar = Rectangle(width=demo["bar_width"], height=current_h, fill_color=bar_color, fill_opacity=0.88, stroke_color=bar_color, stroke_width=2).move_to([demo["bar_x"], demo["bar_bottom"] + current_h / 2, 0])
            new_value = txt(f"I = {current_i:.3f} nA", 25, YELLOW, font="Courier New").move_to([demo["bar_x"], demo["bar_bottom"] + demo["bar_max_h"] + 0.80, 0])
            self.play(
                Transform(demo["tip_body"], new_tip_body),
                Transform(demo["tip_apex"], new_tip_apex),
                Transform(demo["tip_label"], new_tip_label),
                Transform(demo["gap_line"], new_gap_line),
                Transform(demo["gap_label"], new_gap_label),
                Transform(demo["arc"], new_arc),
                Transform(demo["bar"], new_bar),
                Transform(demo["value"], new_value),
                run_time=0.18,
                rate_func=linear,
            )
            current_x = new_x
        self.wait(0.14)
        self.play(FadeOut(arrow), run_time=0.18)
        self.freeze_and_dock(demo["all"], APP_DOCKS[1], INTERMEDIATE_APP_SCALES[1])
        self.docked.append(demo["all"])
        self.play(FadeOut(scrim), run_time=0.34)
        self.remove(scrim)

    def play_cmos(self, tunnel: Mobject) -> None:
        arrow, scrim = self.begin_application(RED)
        demo = make_cmos()
        demo["all"].set_z_index(22)
        self.play(FadeIn(demo["title"], shift=UP * 0.12), Create(demo["rails"]), FadeIn(demo["transistor"]), FadeIn(demo["gauge"]), run_time=0.62)

        rng = np.random.default_rng(42)
        for node, temp, power, fraction in ((4, 58, 4.0, 0.30), (3, 75, 9.0, 0.60), (2, 95, 19.0, 0.92)):
            dots = VGroup()
            animations = []
            for origin in (demo["p_oxide"].get_center(), demo["n_oxide"].get_center()):
                for _ in range(4):
                    dot = Dot(origin, radius=0.065, color=ORANGE)
                    target = origin + np.array([rng.uniform(-0.90, 1.20), rng.uniform(-0.50, 0.50), 0])
                    dots.add(dot)
                    animations.append(dot.animate.move_to(target).set_opacity(0.0))
            self.add(dots)
            new_fill = Arc(radius=demo["gauge_radius"], start_angle=PI, angle=-fraction * PI, arc_center=demo["gauge_center"], color=RED, stroke_width=14)
            new_stats = demo["stats_group"](node, temp, power).shift(STAGE_SHIFT)
            self.play(
                AnimationGroup(*animations, lag_ratio=0.04),
                Transform(demo["gauge_fill"], new_fill),
                Transform(demo["stats"], new_stats),
                run_time=0.62,
                rate_func=ease_in_out_cubic,
            )
            self.remove(dots)

        glow = Circle(radius=2.40, color=RED, fill_color=RED, fill_opacity=0.06, stroke_width=0).move_to(demo["transistor"].get_center())
        self.play(FadeIn(glow), run_time=0.16)
        self.play(glow.animate.set_fill(opacity=0.20), run_time=0.36, rate_func=there_and_back)
        self.remove(glow)
        self.wait(0.12)
        self.play(FadeOut(arrow), run_time=0.18)
        self.freeze_and_dock(demo["all"], APP_DOCKS[2], INTERMEDIATE_APP_SCALES[2])
        self.docked.append(demo["all"])
        self.play(FadeOut(scrim), run_time=0.34)
        self.remove(scrim)


if __name__ == "__main__":
    print("Render TunnellingApplicationsResolveV8 with the Manim CLI.")


