import pygame
from pygame_core.utils import Centerable
from untiy.components.component import Component


class Transform(Component, pygame.Rect, Centerable):
	def __init__(self,
				 position: tuple = (0, 0),
				 size: tuple = (0, 0),
				 parent: Transform | None = None
				 ):
		Component.__init__(self)
		pygame.Rect.__init__(self, position, size)
		self.parent = parent

	def set_position(self, position: tuple):
		parent_size = self.parent.size if self.parent else self.size
		position = super().resolve_pos(position, parent_size, self.size)
		self.topleft = position

	def set_parent(self, parent: Transform):
		if not parent:
			self.parent = parent
			return

		assert isinstance(parent, Transform), "Parent must be a Transform or Rect."
		self.parent = parent

	def update(self): ...

