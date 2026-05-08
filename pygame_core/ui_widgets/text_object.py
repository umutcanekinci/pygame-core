import pygame

from pygame_core.utils import Centerable
from pygame_core.unity.gameobject import GameObject
from pygame_core.unity.components.sprite_renderer2d import SpriteRenderer2D


class TextObject(GameObject, Centerable):
    """A GUI-compatible text label loaded from panel YAML.

    Implements the same minimal interface as GuiObject (draw / handle_event /
    is_clicked / set_state) so PanelManager can treat it uniformly.
    """

    def __init__(
        self,
        parent: tuple[int, int],
        position,
        text: str,
        font: pygame.font.Font,
        color,
        background_color = None,
    ) -> None:
        GameObject.__init__(self)

        self.rect.parent = parent
        self.text = text
        self.font = font
        self.color = color
        self.background_color = background_color

        surface = self.render(text, font, color, background_color)
        self.add_component(SpriteRenderer2D).set_image(surface)
        self.rect.size = surface.get_size()
        self.rect.set_position(position)

    def set_text(self, text: str):
        surface = self.render(text, self.font, self.color, self.background_color)
        self.get_component(SpriteRenderer2D).set_image(surface)

    def render(self, text: str, font, color, background_color):
        return font.render(text, True, self._parse_color(color), self._parse_color(background_color))

    @staticmethod
    def _parse_color(color) -> tuple:
        if color is None:
            return None

        if isinstance(color, (list, tuple)):
            return tuple(color)
        return tuple(pygame.Color(str(color)))