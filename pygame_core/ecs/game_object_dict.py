import pygame
from typing import Any


class GameObjectDict(dict[str, Any]):
    def __init__(self) -> None:
        super().__init__()

    def __getitem__(self, key: str) -> Any:
        return super().__getitem__(key)

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        for obj in self.values():
            if not hasattr(obj, "handle_event"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.handle_event(event, mouse_position)

    def update(self) -> None:  # type: ignore[override]
        for obj in self.values():
            if not hasattr(obj, "update"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.update()

    def draw(self, surface) -> None:
        for obj in self.values():
            if not hasattr(obj, "draw"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.draw(surface)
