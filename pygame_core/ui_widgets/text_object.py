import pygame

from pygame_core.utils import Anchorable
from pygame_core.ecs.game_object import GameObject
from pygame_core.ecs.components.sprite_renderer2d import SpriteRenderer2D


class TextObject(GameObject, Anchorable):
    """A GUI-compatible text label loaded from panel YAML.

    Implements the same minimal interface as GuiObject (draw / handle_event /
    is_clicked / set_state) so PanelManager can treat it uniformly.
    """

    def __init__(
        self,
        parent,
        position,
        text: str,
        font: pygame.font.Font,
        color,
        background_color=None,
        anchor: str = "top-left",
    ) -> None:
        GameObject.__init__(self)

        self.rect.parent = parent
        self.rect.anchor = anchor
        self._position_spec = position
        self.text = text
        self.font = font
        self.color = self._parse_color(color)
        self.background_color = self._parse_color(background_color)

        self.add_component(SpriteRenderer2D)
        self._reflow()

    def set_text(self, text: str) -> None:
        if text == self.text:
            return
        self.text = text
        self._reflow()

    def set_color(self, color) -> None:
        new_color = self._parse_color(color)
        if new_color == self.color:
            return
        self.color = new_color
        self._reflow()

    def render(self, text: str, font, color, background_color):
        return font.render(text, True, color, background_color)

    def _reflow(self) -> None:
        surface = self.render(self.text, self.font, self.color, self.background_color)
        self.get_component(SpriteRenderer2D).set_image(surface)
        self.rect.size = surface.get_size()
        self.rect.set_position(self._position_spec)

    @staticmethod
    def _parse_color(color):
        if color is None:
            return None
        if isinstance(color, (list, tuple)):
            return tuple(color)
        return tuple(pygame.Color(str(color)))