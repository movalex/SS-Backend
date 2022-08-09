from typing import Protocol


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
