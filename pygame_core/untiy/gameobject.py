from __future__ import annotations
from untiy.components.component import Component, Behaviour
from untiy.components.transform import Transform
import pygame

class GameObject:
	def __init__(self, name: str = 'GameObject'):
		self.name = name
		self.active: bool = True
		self.rect: Transform = Transform()
		self.rect.game_object = self
		self._components: dict[str, Component] = {'Transform': self.rect}

	@property
	def game_object(self) -> GameObject:
		return self

	@game_object.setter
	def game_object(self, value): ...

	def add_component(self, component_type: type[Component], **kwargs) -> Component:
		component = component_type(**kwargs)
		component.game_object = self
		self._components[component_type.__name__] = component
		if hasattr(component, 'awake'):
			component.awake()
		return component

	def get_component(self, component_type: type[Component]) -> Component | None:
		return self._components.get(component_type.__name__)

	def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
		if not self.active: return

		for component in self._components.values():
			enabled = not isinstance(component, Behaviour) or component.enabled
			if enabled and hasattr(component, 'handle_event'):
				component.handle_event(event, mouse_position)


	def update(self):
		if not self.active: return

		for component in self._components.values():
			enabled = not isinstance(component, Behaviour) or component.enabled
			if enabled and hasattr(component, 'update'):
				component.update()

	def draw(self, surface: pygame.Surface) -> None:
		if not self.active: return

		for component in self._components.values():
			enabled = not isinstance(component, Behaviour) or component.enabled
			if enabled and hasattr(component, 'draw'):
				component.draw(surface)