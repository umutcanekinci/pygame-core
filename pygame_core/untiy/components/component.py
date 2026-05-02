from __future__ import annotations


class Component:
	def __init__(self):
		self.game_object = None

	def get_component(self, component_type: type[Component]) -> Component | None:
		return self.game_object.get_component(component_type)


class Behaviour(Component):
	def __init__(self):
		super().__init__()
		self.enabled: bool = True


class MonoBehaviour(Behaviour):
	def awake(self): ...
	def start(self): ...
	def update(self): ...
	def on_destroy(self): ...