from __future__ import annotations

import pygame

from pygame_core.ecs.game_object import GameObject


class Mouse:
    def __init__(self, tile_size=None) -> None:
        self.position = (0, 0)
        self.tile_size = tile_size
        self.cursor: GameObject | None = None
        # physical (real OS window) -> logical (game's design resolution)
        # factor; Application keeps this in sync whenever the actual window
        # size changes, since the game always thinks in logical coordinates.
        self.scale = (1.0, 1.0)

        if self.tile_size:
            self.tile_pos = (0, 0)

    @staticmethod
    def set_cursor_visible(value=True) -> None:
        pygame.mouse.set_visible(value)

    def set_cursor_image(self, image) -> None:
        self.cursor = image

    def update(self) -> None:
        raw_x, raw_y = pygame.mouse.get_pos()
        scale_x, scale_y = self.scale
        self.position = (raw_x * scale_x, raw_y * scale_y)

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