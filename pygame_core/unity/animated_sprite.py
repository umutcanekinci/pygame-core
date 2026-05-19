"""AnimatedSprite + factory: GameObject preconfigured with SpriteRenderer2D and
Animator for sheet-based animation.

	factory = AnimatedSpriteFactory(assets)
	coin    = factory.from_strip("coin_sheet", (x, y), frame_count=4, fps=8)
	coin.update(); coin.draw(surface)
"""
from typing import cast

import pygame

from pygame_core.sprite_sheet import SpriteSheet
from pygame_core.unity.components.animator import Animator, AnimationClip
from pygame_core.unity.components.sprite_renderer2d import SpriteRenderer2D
from pygame_core.unity.gameobject import GameObject


class AnimatedSprite(GameObject):
	"""GameObject with a SpriteRenderer2D + Animator preconfigured.

	The initial set of frames is registered as the "default" clip and starts
	playing immediately. Additional clips can be added via add_clip().
	"""

	def __init__(self,
				 position: tuple[int, int],
				 frames: list[pygame.Surface],
				 fps: float = 12.0,
				 loop: bool = True,
				 name: str = "animated_sprite") -> None:
		if not frames:
			raise ValueError("AnimatedSprite requires at least one frame")
		super().__init__(name=name)

		self.rect.size = frames[0].get_size()
		self.rect.center = position

		self.add_component(SpriteRenderer2D)
		self.animator = cast(Animator, self.add_component(Animator))
		self.animator.add_clip("default", AnimationClip(frames, fps=fps, loop=loop))
		self.animator.play("default")

	def add_clip(self, name: str, frames: list[pygame.Surface], fps: float = 12.0, loop: bool = True) -> None:
		self.animator.add_clip(name, AnimationClip(frames, fps=fps, loop=loop))

	def play(self, name: str, restart: bool = False) -> None:
		self.animator.play(name, restart=restart)


class AnimatedSpriteFactory:
	"""Builds AnimatedSprite instances from AssetManager-registered spritesheets."""

	def __init__(self, assets):
		self._assets = assets

	def from_strip(self,
				   asset_key: str,
				   position: tuple[int, int],
				   frame_count: int,
				   fps: float = 12.0,
				   loop: bool = True,
				   horizontal: bool = True,
				   name: str | None = None) -> AnimatedSprite:
		sheet  = SpriteSheet.from_path(self._assets.image_path(asset_key))
		frames = sheet.strip(frame_count, horizontal=horizontal)
		return AnimatedSprite(position, frames, fps=fps, loop=loop, name=name or asset_key)

	def from_grid(self,
				  asset_key: str,
				  position: tuple[int, int],
				  cols: int,
				  rows: int,
				  fps: float = 12.0,
				  loop: bool = True,
				  name: str | None = None) -> AnimatedSprite:
		sheet  = SpriteSheet.from_path(self._assets.image_path(asset_key))
		frames = sheet.grid(cols, rows)
		return AnimatedSprite(position, frames, fps=fps, loop=loop, name=name or asset_key)