import pygame


class GameObjectList(list):
    def __init__(self) -> None:
        super().__init__()

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        for obj in self:
            if not hasattr(obj, "handle_event"): continue

            obj.handle_event(event, mouse_position)

    def update(self) -> None:
        for obj in self:
            if not hasattr(obj, "update"): continue

            obj.update()

    def draw(self, surface) -> None:
        for obj in self:
            if not hasattr(obj, "draw"): continue

            obj.draw(surface)
