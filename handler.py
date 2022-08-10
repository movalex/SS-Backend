from __future__ import annotations
from dataclasses import dataclass
import tkinter as tk
from .gui import GUI, Rectangle
from .style import colors
from .controller import Controller


def is_within(coords: tuple[float, float], area: dict[tuple[float, float]]) -> bool:
    x, y = coords[0], coords[1]
    if x <= area["top_left"][0]:
        return False
    if x >= area["top_right"][0]:
        return False
    if y >= area["top_left"][1]:
        return False
    if y <= area["bottom_left"][1]:
        return False
    return True


def find_grid_block_within(
    coords: tuple[float, float], grid_blocks: list[Rectangle]
) -> Rectangle:
    return next(
        (block for block in grid_blocks if is_within(coords, block.corners)),
        None,
    )


def get_event_coords_normalized(event: tk.Event) -> tuple[float, float]:
    self: tk.Widget = event.widget
    coords = (event.x / self.winfo_width(), 1 - event.y / self.winfo_height())
    return coords


@dataclass
class EventHandler:
    """Responsible for getting input from user interaction and passing it along to the Controller."""

    controller: Controller
    gui: GUI

    def __post_init__(self):
        self.gui.handler = self
        self.new_screen_coords: tuple[float, float] = None
        self.new_screen_indexes: tuple[int, int] = None
        self.gui.bind("<Button-1>", self.on_click_canvas, add="+")
        self.gui.bind("<ButtonRelease-1>", self.on_release_canvas, add="+")

    def on_change_setting(self=None, key: str = None, var: tk.IntVar = None) -> None:
        self.controller.change_setting(key, var.get())

    # Click and Drag on Canvas ================================================
    def on_click_canvas(self, event: tk.Event) -> None:
        canvas: GUI = event.widget

        item = canvas.find_closest(event.x, event.y)
        if canvas.itemcget(item, "fill") == colors.CANVAS_SCREEN:
            self.new_screen_coords = None
            return

        coords = get_event_coords_normalized(event)
        self.new_screen_coords = coords
        block = find_grid_block_within(coords, canvas.grid_blocks)

        if block is not None:
            index = block.index
            self.new_screen_indexes = index
            return
        self.new_screen_indexes = None

    def on_release_canvas(self, event: tk.Event) -> None:
        if self.new_screen_coords is None:
            return

        canvas: GUI = event.widget

        coords = get_event_coords_normalized(event)

        self.new_screen_coords = (self.new_screen_coords, coords)

        block = find_grid_block_within(coords, canvas.grid_blocks)
        if block is not None:
            index = block.index
            self.new_screen_indexes = (self.new_screen_indexes, index)
            self.controller.do_command("add_screen", self.new_screen_indexes)
            return

        self.new_screen_indexes = None

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

    def on_pre_delete_all(self, event: tk.Event) -> None:
        canvas = self.gui
        canvas.itemconfig(
            "screen",
            fill=colors.CANVAS_SCREEN_PRE_DELETE,
            outline=colors.CANVAS_SCREEN_PRE_DELETE,
        )

    def on_delete_all(self, event: tk.Event) -> None:
        self.controller.do_command("delete_all_screens")
