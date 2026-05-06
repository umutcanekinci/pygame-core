import pygame


class MouseInteractive:
    """is_mouse_over, is_clicked davranışını ekler."""
    rect: pygame.Rect
    parent: object  # opsiyonel, parent objenin rect'ini de dahil etmek için
    visible: bool = True

    # Press tracking için instance state
    _pressed: bool = False

    def is_mouse_over(self, mouse_pos):
        rect = self.parent.rect + self.rect if hasattr(self, "parent") else self.rect
        return mouse_pos is not None and rect.collidepoint(mouse_pos) and self.visible

    def is_clicked(self, event, mouse_pos):
        pressed = getattr(self, "_pressed", False)

        """True döner: mouse bu obje üzerinde basıldı VE üzerinde bırakıldı."""
        if not self.visible:
            self._pressed = False
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_mouse_over(mouse_pos):
                self._pressed = True
            return False

        if event.type == pygame.MOUSEBUTTONUP:
            was_pressed = self._pressed
            self._pressed = False  # her zaman reset
            return was_pressed and event.button == 1 and self.is_mouse_over(mouse_pos)

        return False

def resolve_size(size, window_size):
    if size == "WINDOW":
        return tuple(window_size)
    if isinstance(size, list) and len(size) == 2:
        return tuple(size)
    raise ValueError(f"Invalid size: {size!r}")

class Centerable:
    """CENTER konum çözümleme."""

    @staticmethod
    def resolve_pos(pos, window_size, obj_size):
        x, y = pos
        if x == "CENTER": x = (window_size[0] - obj_size[0]) / 2
        if y == "CENTER": y = (window_size[1] - obj_size[1]) / 2
        return (x, y)