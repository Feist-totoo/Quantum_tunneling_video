"""Small, localized UI fallbacks for Resolve operations absent from its API.

This is intentionally limited to operations that Resolve 20 exposes only in
the desktop interface. Normal editing remains on the Resolve scripting bridge.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from pywinauto import Desktop, keyboard


POPUP_CLASS_FRAGMENT = "QWindowPopupDropShadowSaveBits"


def main_window():
    candidates = [
        window
        for window in Desktop(backend="uia").windows()
        if window.class_name() == "UiMainWindowImp"
        and window.window_text() in {"Resolve", "DaVinci Resolve"}
    ]
    if not candidates:
        raise RuntimeError("DaVinci Resolve main window not found")
    return candidates[0]


def visible_popups():
    return [
        window
        for window in Desktop(backend="win32").windows()
        if POPUP_CLASS_FRAGMENT in window.class_name() and window.is_visible()
    ]


def close_menus() -> None:
    keyboard.send_keys("{ESC}{ESC}{ESC}")
    time.sleep(0.2)


def open_top_menu(window, title: str):
    close_menus()
    window.set_focus()
    top_item = next(
        item for item in window.descendants(control_type="MenuItem") if item.window_text() == title
    )
    top_item.click_input()
    time.sleep(0.3)
    matches = [
        popup
        for popup in visible_popups()
        if abs(popup.rectangle().left - top_item.rectangle().left) <= 4
    ]
    if not matches:
        raise RuntimeError(f"popup for top menu {title!r} not found")
    popup = max(matches, key=lambda item: item.rectangle().height())
    return Desktop(backend="uia").window(handle=popup.handle)


def run_bridge() -> None:
    window = main_window()
    workspace = open_top_menu(window, "工作区")
    scripts = next(
        item for item in workspace.descendants(control_type="MenuItem") if item.window_text() == "脚本"
    )
    scripts.move_mouse_input()
    time.sleep(0.5)
    other_popups = [
        popup
        for popup in visible_popups()
        if popup.handle != workspace.handle and popup.rectangle().left >= workspace.rectangle().right - 5
    ]
    if not other_popups:
        scripts.click_input()
        time.sleep(0.5)
        other_popups = [
            popup
            for popup in visible_popups()
            if popup.handle != workspace.handle and popup.rectangle().left >= workspace.rectangle().right - 5
        ]
    if not other_popups:
        raise RuntimeError("Workspace > Scripts submenu did not open")
    popup = Desktop(backend="uia").window(handle=other_popups[0].handle)
    items = popup.descendants(control_type="MenuItem")
    bridge = next((item for item in items if "resolve_bridge" in item.window_text().casefold()), None)
    if bridge is None:
        available = [item.window_text() for item in items]
        raise RuntimeError(f"resolve_bridge is not in Scripts menu: {available}")
    bridge.click_input()
    time.sleep(1.5)
    print("resolve_bridge launched")


def screenshot(path: str) -> None:
    window = main_window()
    window.set_focus()
    time.sleep(0.4)
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    window.capture_as_image().save(output_path)
    print(f"Resolve screenshot written to {output_path}")


def cli() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["run_bridge", "screenshot"])
    parser.add_argument("--path")
    args = parser.parse_args()
    if args.action == "run_bridge":
        run_bridge()
    elif args.action == "screenshot":
        if not args.path:
            parser.error("screenshot requires --path")
        screenshot(args.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
