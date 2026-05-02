from pygame import Vector2
from untiy.components.component import Component

class Rigidbody2D(Component):
	def __init__(self):
		super().__init__()
		self.velocity = Vector2(0, 0)
		self._float_pos = None

	def set_velocity(self, velocity: tuple):
		self.velocity = Vector2(velocity)

	def update(self) -> None:
		transform = self.game_object.rect
		if self._float_pos is None:
			self._float_pos = Vector2(transform.topleft)
		self._float_pos += self.velocity
		transform.topleft = (round(self._float_pos.x), round(self._float_pos.y))