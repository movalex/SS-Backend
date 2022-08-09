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

        self.commands: dict[str, dict[str, function]] = {
            "width": {
                "getter": self.grid.canvas.get_width,
                "setter": self.grid.canvas.set_width,
            },
            "height": {
                "getter": self.grid.canvas.get_height,
                "setter": self.grid.canvas.set_height,
            },
            "margin": {
                "getter": self.grid.margin.get_top,  # When margins are linked, they'll all
                "setter": self.grid.margin.set_all,  # automatically be the same.
            },
            "top": {
                "getter": self.grid.margin.get_top,
                "setter": self.grid.margin.set_top,
            },
            "left": {
                "getter": self.grid.margin.get_left,
                "setter": self.grid.margin.set_left,
            },
            "bottom": {
                "getter": self.grid.margin.get_bottom,
                "setter": self.grid.margin.set_bottom,
            },
            "right": {
                "getter": self.grid.margin.get_right,
                "setter": self.grid.margin.set_right,
            },
            "gutter": {
                "getter": self.grid.margin.get_gutter,
                "setter": self.grid.margin.set_gutter,
            },
            "cols": {
                "getter": self.grid.get_cols,
                "setter": self.grid.set_cols,
            },
            "rows": {
                "getter": self.grid.get_rows,
                "setter": self.grid.set_rows,
            },
            "add_screen": self.add_screen,
            "delete_screen": self.delete_screen,
            "flip_h": self.flip_h,
            "flip_v": self.flip_v,
            "delete_all_screens": self.delete_all_screens,
        }

    def do_command(self, key: str, value: int | None = None) -> None:
        command = self.commands[key]
        command(value)

    def change_setting(self, key: str, value: int) -> None:
        getter = self.commands[key]["getter"]
        setter = self.commands[key]["setter"]

        if getter() == value:
            return

        setter(value)

        self.refresh_resolve_api()
        self.refresh_ui()

    # Refreshers
    def refresh_ui(self):
        rects = self.ui.refresh()
        self.update_screen_rect_ids(rects)

    def refresh_resolve_api(self):

        self.resolve_api.refresh_global(
            self.canvas_resolution, self.screen_tools, self.screen_values
        )

    # Screen Manipulation  ====================================================
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

    # Transformations  ===================================================
    def flip_h(self):
        ...

    def flip_v(self):
        ...

    # Changes in self  ========================================================
    def update_screen_rect_ids(self, ids: list[int] | None) -> None:
        """When screens are redrawn by the UI, their rectangle ids change."""
        if ids is None:  # Means there are still no screens.
            return

        for screen_dict, id in zip(self.screens.values(), ids):
            screen_dict["rectangle"] = id

    # Useful Properties  ======================================================
    @property
    def screen_values(self) -> list[dict[str, float]]:
        return [screen_dict["screen"].values for screen_dict in self.screens.values()]

    @property
    def canvas_resolution(self) -> tuple[int, int]:
        return self.grid.canvas.resolution

    @property
    def screen_tools(self) -> list[tuple[Tool, Tool]]:
        return [
            (screen_dict["tools"][0], screen_dict["tools"][1])
            for screen_dict in self.screens.values()
        ]
