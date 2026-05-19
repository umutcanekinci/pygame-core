"""SpriteSheet: slice a single image into a list of frame surfaces.

Pairs naturally with pygame_core.unity.components.animator.AnimationClip:

    sheet  = SpriteSheet.from_path("coin_strip4.png")
    frames = sheet.strip(4)
    clip   = AnimationClip(frames, fps=8, loop=True)
"""
import pygame
from pygame_core.asset_path import PathLike
from pygame_core.image import load_image


class SpriteSheet:
	def __init__(self, image: pygame.Surface):
		self.image = image

	@classmethod
	def from_path(cls, path: PathLike) -> "SpriteSheet":
		return cls(load_image(path))

	def strip(self, frame_count: int, horizontal: bool = True) -> list[pygame.Surface]:
		"""Slice an evenly-divided single-row (or single-column) strip into N frames."""
		if frame_count <= 0:
			return []
		w, h = self.image.get_size()
		if horizontal:
			fw, fh = w // frame_count, h
			return [self.image.subsurface((i * fw, 0, fw, fh)) for i in range(frame_count)]
		fw, fh = w, h // frame_count
		return [self.image.subsurface((0, i * fh, fw, fh)) for i in range(frame_count)]

	def grid(self, cols: int, rows: int) -> list[pygame.Surface]:
		"""Slice an evenly-divided grid; returns frames in row-major order."""
		if cols <= 0 or rows <= 0:
			return []
		w, h = self.image.get_size()
		fw, fh = w // cols, h // rows
		return [
			self.image.subsurface((c * fw, r * fh, fw, fh))
			for r in range(rows)
			for c in range(cols)
		]

	def frame(self, col: int, row: int, frame_w: int, frame_h: int) -> pygame.Surface:
		"""Pull a single frame at a grid coord, given the source-pixel frame size."""
		return self.image.subsurface((col * frame_w, row * frame_h, frame_w, frame_h))