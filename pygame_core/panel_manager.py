import pygame


class PanelManager(dict):
    def __init__(self, background_colors=None) -> None:
        super().__init__()
        self.background_colors = background_colors
        self.tab = ""

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        if self.tab in self:
            for obj in self[self.tab].values():
                obj.handle_events(event, mouse_position)

    def add_object(self, tab: str, name: str, obj) -> None:
        self.add_tab(tab)
        self[tab][name] = obj

    def add_tab(self, name: str) -> None:
        if name not in self:
            self[name] = {}

    def open_tab(self, tab: str) -> None:
        self.tab = tab

    def draw(self, surface) -> None:
        if self.background_colors and self.tab in self.background_colors:
            surface.fill(self.background_colors[self.tab])

        if self.tab in self:
            for obj in self[self.tab].values():
                obj.draw(surface)