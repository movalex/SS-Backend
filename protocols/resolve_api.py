from typing import Protocol


class ResolveAPI(Protocol):
    def refresh_global(self) -> None:
        """Calls all necessary methods for when user changes settings to grid, margin or canvas."""
        raise NotImplementedError()

    def refresh_positions(self) -> None:
        """Calls all necessary methods for when user deletes screens."""
        raise NotImplementedError()

    def add_canvas(self, width: int, height: int) -> None:
        raise NotImplementedError()

    def add_screen(self) -> None:
        raise NotImplementedError()

    def delete_screen(self) -> None:
        raise NotImplementedError()

    def delete_all_screens(self) -> None:
        raise NotImplementedError()
