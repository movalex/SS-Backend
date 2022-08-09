from .classes import Grid, Screen
from .protocols import ResolveAPI, UI
from .fusion_alias import Tool
from .utils import find_first_missing


class Controller:
    """Responsible for receiving inputs and executing commands"""

    def __init__(self, grid: Grid, resolve_api: ResolveAPI, ui: UI) -> None:
        self.grid = grid
        self.resolve_api = resolve_api
        self.ui = ui

        self.screens: dict[int, dict[str, Screen | tuple[Tool, Tool, Tool] | int]] = {}

        self.commands: dict[str, function] = {
            "width": self.set_width,
            "height": self.set_height,
            "margin": self.set_margin,
            "top": self.set_top,
            "left": self.set_left,
            "bottom": self.set_bottom,
            "right": self.set_right,
            "gutter": self.set_gutter,
            "cols": self.set_cols,
            "rows": self.set_rows,
            "add_screen": self.add_screen,
            "delete_screen": self.delete_screen,
            "flip_h": self.flip_h,
            "flip_v": self.flip_v,
            "delete_all_screens": self.delete_all_screens,
        }

    def do_command(self, key: str, value: int | None = None) -> None:
        print(f"Doing command {key}... Setting to {value}")
        command = self.commands[key]
        command(value)

    @property
    def screen_values(self) -> list[dict[str, float]]:
        return [screen_dict["screen"].values for screen_dict in self.screens.values()]

    @property
    def canvas_resolution(self) -> tuple[int, int]:
        return self.grid.canvas.resolution

    def refresh_resolve_api(self):
        screen_tools: list[tuple[Tool, Tool]] = [
            screen_dict["tools"][0, 1] for screen_dict in self.screens.values()
        ]

        screen_values = self.screen_values

        self.resolve_api.refresh_global(
            self.canvas_resolution, screen_tools, screen_values
        )
        ...

    # Changes in Canvas =======================================================
    def set_width(self, value: int) -> None:
        if self.grid.canvas.width == value:
            return
        self.grid.canvas.width = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def set_height(self, value: int) -> None:
        if self.grid.canvas.height == value:
            return
        self.grid.canvas.height = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    # Changes in Margin =======================================================
    def set_margin(self, value: int) -> None:
        mg = self.grid.margin
        if mg._top_px == mg._left_px == mg._bottom_px == mg._right_px == value:
            return

        self.grid.margin.all = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def set_top(self, value: int) -> None:
        if self.grid.margin._top_px == value:
            return

        self.grid.margin.top = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def set_left(self, value: int) -> None:
        if self.grid.margin._left_px == value:
            return

        self.grid.margin.left = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def set_bottom(self, value: int) -> None:
        if self.grid.margin._bottom_px == value:
            return

        self.grid.margin.bottom = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def set_right(self, value: int) -> None:
        if self.grid.margin._right_px == value:
            return

        self.grid.margin.right = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def set_gutter(self, value: int) -> None:
        if self.grid.margin._gutter_px == value:
            return

        self.grid.margin.gutter = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    # Changes in Grid =========================================================
    def set_cols(self, value: int) -> None:
        if self.grid.cols == value:
            return

        self.grid.cols = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def set_rows(self, value: int) -> None:
        if self.grid.rows == value:
            return

        self.grid.rows = value
        self.resolve_api.refresh_global(self.canvas_resolution, self.screen_values)

        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    # Changes in Screens ======================================================
    def add_screen(self, coords: tuple[int, int]):
        new_key = find_first_missing(self.screens.keys())

        screen = Screen.create_from_coords(self.grid, *coords)
        tools: tuple[Tool, Tool, Tool] = self.resolve_api.add_screen(screen.values)
        rect = self.ui.draw_screen(screen.values)

        new_screen_dict = {"screen": screen, "tools": tools, "rectangle": rect}

        self.screens[new_key] = new_screen_dict

    def find_screen_by_rect_id(self, rect_id) -> int:
        return [
            id
            for id, screen_dict in self.screens.items()
            if screen_dict["rectangle"] == rect_id
        ][0]

    def delete_screen(self, rect_id: int):
        id = self.find_screen_by_rect_id(rect_id)
        screen, tools, rect = self.screens[id].values()

        self.grid.screens.remove(screen)
        self.resolve_api.delete_screen(tools)
        self.ui.undraw_screens(rect)

        self.screens[id] = None

    def delete_all_screens(self):
        rects = []
        for screen_dict in self.screens:
            screen = screen_dict["screen"]
            self.grid.screens.remove(screen)

            rect = screen_dict["rectangle"]
            rects.append(rect)

        self.ui.undraw_screens(*rects)

        self.resolve_api.delete_all_screens()  # Fusion automatically keeps track

        self.screens.clear()

    # Full Transformations ====================================================
    def flip_h(self):
        ...

    def flip_v(self):
        ...

    # Changes in self =========================================================
    def update_screen_rect_ids(self, ids: list[int] | None) -> None:
        """When screens are redrawn by the UI, their rectangle ids change."""
        if ids is None:  # Means there are still no screens.
            return

        for screen_dict, id in zip(self.screens.values(), ids):
            screen_dict["rectangle"] = id
