import pygame
from untiy.components.component import Component
from untiy.components.transform import Transform


class SpriteRenderer2D(Component):
	def __init__(self):
		super().__init__()
		self.image: pygame.Surface | None = None

	def set_image(self, image: pygame.Surface):
		self.image = image

	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.image, super().get_component(Transform))