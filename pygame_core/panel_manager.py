import pygame
from pygame_core.unity.game_object_dict import GameObjectDict


class PanelManager(dict[str, GameObjectDict]):
    def __init__(self, background_colors=None, starting_tab="") -> None:
        super().__init__()
        self.background_colors = background_colors
        self.current_panel = starting_tab

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        if self.current_panel not in self: return

        self[self.current_panel].handle_event(event, mouse_position)

    def update(self) -> None:
        if self.current_panel not in self: return

        self[self.current_panel].update()

    def draw(self, surface) -> None:
        if self.background_colors and self.current_panel in self.background_colors:
            surface.fill(self.background_colors[self.current_panel])

        if self.current_panel not in self: return

        self[self.current_panel].draw(surface)

    def add_object(self, panel: str, name: str, obj) -> None:
        self.add_panel(panel)
        self[panel][name] = obj

    def add_object_to_all(self, panels: tuple[str], name: str, obj) -> None:
        for panel in panels:
            self.add_object(panel, name, obj)

    def add_panel(self, name: str) -> None:
        if name in self: return

        self[name] = GameObjectDict()

    def open_panel(self, panel: str) -> None:
        self.current_panel = panel