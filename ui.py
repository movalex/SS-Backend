from __future__ import annotations
from typing import Protocol
from typing_extensions import Self
from .classes import Grid, GridCell
from dataclasses import dataclass
import tkinter as tk
from .style import colors


@dataclass
class Rectangle:
    """A tk.Canvas item that represents a SplitScreener Screen on the GUI.
    It translates Fusion coordinates to tk coordinates and feeds them to its
    parent canvas so it can be drawn."""

    parent: tk.Canvas
    screen_values: dict[str, float | list[float]]

    def compute(self) -> Self:
        width, height, center, size = self.screen_values.values()
        x, y = center
        y = 1 - y
        canvas_width, canvas_height = (
            self.parent.winfo_width(),
            self.parent.winfo_height(),
        )

        self.x0 = (x - width / 2) * canvas_width
        self.y0 = (y - height / 2) * canvas_height
        self.x1 = self.x0 + width * canvas_width
        self.y1 = self.y0 + height * canvas_height

        return self

    def draw(self, **settings) -> int:
        rectangle = self.parent.create_rectangle(
            self.x0, self.y0, self.x1, self.y1, **settings
        )
        return rectangle


class HandlerNotAttachedError(Exception):
    pass


class UI(Protocol):
    def draw_grid(self) -> None:
        raise NotImplementedError()

    def draw_screen(self, screen_values: dict[str, float]) -> int:
        raise NotImplementedError()

    def undraw_screens(self, *ids: int) -> None:
        raise NotImplementedError()

    def refresh(self, screen_values: list[dict[str, float]] | None) -> list[int] | None:
        """
        Refreshes grid and user created screens if there are any.
        In that case, returns a list of their new rectangle IDs.
        """
        raise NotImplementedError()


class ScreenSplitterUI(tk.Canvas):
    def __init__(
        self,
        master: tk.Widget,
        ss_grid: Grid,
        max_width: tk.IntVar,
        max_height: tk.IntVar,
    ):
        super().__init__(master)
        self.ss_grid = ss_grid
        self.max_width = max_width
        self.max_height = max_height

        self.grid_blocks: list[int] = None
        self.handler = None

        self.config(
            background=colors.CANVAS_BG,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )

    # PROTOCOL METHODS  =======================================================
    def draw_grid(self) -> None:
        print(
            f"about to generate grid cells for a {self.ss_grid.canvas.resolution} grid."
        )
        grid_cells = GridCell.generate_all(self.ss_grid)

        rects: list[Rectangle] = []
        for cell in grid_cells:
            rect = Rectangle(self, cell.values)
            rects.append(rect)

        rect_ids: list[int] = []
        for rect in rects:
            rect_id = rect.compute().draw(
                fill=colors.CANVAS_BLOCK,
                activefill=colors.CANVAS_BLOCK_HOVER,
                outline=colors.CANVAS_BLOCK,
                activeoutline=colors.CANVAS_BLOCK,
                activewidth=1,
            )
            rect_ids.append(rect_id)
        print("just drew grid cells.")

        self.grid_blocks = rect_ids

    def draw_screen(self, screen_values: dict[str, float | list[float]]) -> int:
        rect = Rectangle(self, screen_values)
        rect_id = rect.compute().draw(
            fill=colors.CANVAS_SCREEN, outline=colors.CANVAS_SCREEN, tag="screen"
        )

        self.bind_screen(rect_id)

        return rect_id

    def undraw_screens(self, *ids: int) -> None:
        self.delete(*ids)

    def refresh(
        self, screen_values: list[dict[str, float]] | None = None
    ) -> list[int] | None:
        """
        Refreshes grid and user created screens if there are any.
        In that case, returns a list of their new rectangle IDs.
        """

        self.delete("screen")
        self.delete(*self.grid_blocks)

        self.draw_canvas()
        self.draw_grid()

        rect_ids: list[int] = None
        if screen_values:
            rect_ids = []
            for values in screen_values:
                rect_id = self.draw_screen(values)
                rect_ids.append(rect_id)

        return rect_ids

    # =========================================================================

    # Other Methods  ==========================================================
    def bind_screen(self, id: int):
        if not self.handler:
            print("Please attach an event handler first.")
            raise HandlerNotAttachedError()

        self.tag_bind(id, "<Button-2>", self.handler.on_pre_delete_screen)
        self.tag_bind(
            id,
            "<Button-2> <Leave>",
            lambda e: self.handler.on_cancel_screen_deletion(id=id),
        )
        self.tag_bind(id, "<Button-2> <ButtonRelease-2>", self.handler.on_delete_screen)

    # Self drawing funcs
    def compute_canvas_dimensions(self) -> tuple[int]:
        canvas = self.ss_grid.canvas
        aspect_ratio = canvas.aspect_ratio

        max_width = self.max_width
        max_height = self.max_height

        if aspect_ratio > 1:
            canvas_width = max_width
            canvas_height = canvas_width / aspect_ratio
        else:
            canvas_height = max_height
            canvas_width = canvas_height * aspect_ratio

        return canvas_width, canvas_height

    def draw_canvas(self) -> None:
        canvas_width, canvas_height = self.compute_canvas_dimensions()
        self.config(width=canvas_width, height=canvas_height)
