"""Font loading helper used by panel factories.

Looks up `cfg[font_key]` in the asset manifest first; if no font is registered
under that name, treats it as a system font and falls back to SysFont.
"""
import pygame


def load_font(cfg: dict, assets, font_key: str = "font", size_key: str = "font_size") -> pygame.font.Font:
	name = cfg.get(font_key, "Arial")
	size = cfg.get(size_key, 32)
	try:
		return pygame.font.Font(str(assets.font_path(name)), size)
	except KeyError:
		return pygame.font.SysFont(name, size)
