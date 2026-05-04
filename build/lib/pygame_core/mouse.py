import pygame
from state_object import StateObject


class Mouse:
    def __init__(self, tile_size=None) -> None:
        self.position = (0, 0)
        self.tile_size = tile_size
        self.cursor: StateObject = None

        if self.tile_size:
            self.tile_pos = (0, 0)

    @staticmethod
    def set_cursor_visible(value=True) -> None:
        pygame.mouse.set_visible(value)

    def set_cursor(self, image) -> None:
        self.cursor = image

    def update(self) -> None:
        self.position = pygame.mouse.get_pos()

        if self.tile_size:
            self.tile_pos = (self.position[0] // self.tile_size, self.position[1] // self.tile_size)

        if self.cursor:
            self.cursor.rect.set_position(self.position)

    def draw(self, window: pygame.Surface) -> None:
        if self.cursor:
            self.cursor.draw(window)

    def get_info(self):
        return "Mouse Info:", {
            "pos": self.position,
            "tile_pos": self.tile_pos if self.tile_size else None
        }