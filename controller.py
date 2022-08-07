from dataclasses import dataclass
from .classes import Grid
from .protocols import ResolveAPI, UI


@dataclass
class Controller:
    grid: Grid
    resolve_api: ResolveAPI
    ui: UI

    def user_request(self, key: str, value: int) -> None:
        raise NotImplementedError()
