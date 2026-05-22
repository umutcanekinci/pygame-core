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
        padding=None,
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
        self.padding = self._parse_padding(padding)

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

    def _reflow(self) -> None:
        text_surface = self.font.render(self.text, True, self.color)
        top, right, bottom, left = self.padding

        if self.background_color is None and self.padding == (0, 0, 0, 0):
            surface = text_surface
        else:
            tw, th = text_surface.get_size()
            surface = pygame.Surface((tw + left + right, th + top + bottom), pygame.SRCALPHA)
            if self.background_color is not None:
                surface.fill(self.background_color)
            surface.blit(text_surface, (left, top))

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

    @staticmethod
    def _parse_padding(padding):
        """CSS-style: int -> all sides; [v, h]; [top, right, bottom, left]."""
        if padding is None:
            return (0, 0, 0, 0)
        if isinstance(padding, (int, float)):
            p = int(padding)
            return (p, p, p, p)
        if isinstance(padding, (list, tuple)):
            vals = [int(v) for v in padding]
            if len(vals) == 1:
                p = vals[0]
                return (p, p, p, p)
            if len(vals) == 2:
                v, h = vals
                return (v, h, v, h)
            if len(vals) == 4:
                return tuple(vals)
        raise ValueError(f"Invalid padding: {padding!r} (expected int, [v,h], or [top,right,bottom,left])")