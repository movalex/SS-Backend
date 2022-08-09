from __future__ import annotations
from dataclasses import dataclass
import tkinter as tk

from ss_backend.protocols.ui import UI
from .style import colors
from .controller import Controller


@dataclass
class EventHandler:
    """Responsible for getting input from user interaction and passing it along to the Controller."""

    controller: Controller
    ui: UI

    def __post_init__(self):
        self.ui.handler = self

    def on_change_setting(self=None, key: str = None, var: tk.IntVar = None) -> None:
        self.controller.change_setting(key, var.get())

    # Click and Drag on Canvas ================================================
    def on_click_canvas(self, event: tk.Event) -> None:
        ...  # register first coord

    def on_release_canvas(self, event: tk.Event) -> None:
        ...  # register second coord
        coords: tuple[int, int] = ...
        self.controller.do_command("add_screen", coords)

    # Deleting Screens ========================================================
    user_wants_to_delete: bool = True

    def on_pre_delete_screen(self, event: tk.Event) -> None:
        canvas: tk.Canvas = event.widget
        rect_id = canvas.find_closest(event.x, event.y)[0]
        canvas.itemconfig(
            rect_id,
            fill=colors.CANVAS_SCREEN_PRE_DELETE,
            outline=colors.CANVAS_SCREEN_PRE_DELETE,
        )

    def on_delete_screen(self, event: tk.Event) -> None:
        if not self.user_wants_to_delete:
            self.user_wants_to_delete = True
            return "break"

        canvas: tk.Canvas = event.widget
        rect_id = canvas.find_closest(event.x, event.y)[0]

        self.controller.do_command("delete_screen", rect_id)

    def on_cancel_screen_deletion(self, event: tk.Event, id: int = None) -> None:
        canvas: tk.Canvas = event.widget
        self.user_wants_to_delete = False
        canvas.itemconfig(id, fill=colors.CANVAS_SCREEN, outline=colors.CANVAS_SCREEN)

    # Transformations on Right Button Frame ===================================
    def on_flip_h(self, event: tk.Event) -> None:
        self.controller.do_command("flip_h")

    def on_flip_v(self, event: tk.Event) -> None:
        self.controller.do_command("flip_v")

    def on_rotate_cw(self, event: tk.Event) -> None:
        self.controller.do_command("rotate_cw")

    def on_rotate_ccw(self, event: tk.Event) -> None:
        self.controller.do_command("rotate_ccw")

    def on_delete_all(self, event: tk.Event) -> None:
        self.controller.do_command("delete_all_screens")
