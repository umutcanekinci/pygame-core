#-# Importing Packages #-#
import pygame
from pygame_core.asset_path import *

#-# Image Loading Function #-#
def load_image(path, size=None, return_size=False):
	img = pygame.image.load(path).convert_alpha()

	if size is None:
		size = [0, 0]
	elif isinstance(size, tuple):
		size = list(size)

	if size == [0, 0]:
		return (img, list(img.get_size())) if return_size else img

	if size[0] == 0:   size[0] = img.get_width()
	if size[1] == 0:   size[1] = img.get_height()
	if size[0] == 1 / 3: size[0] = img.get_width() // 5
	if size[1] == 1 / 3: size[1] = img.get_height() // 5

	scaled = pygame.transform.scale(img, size)
	return (scaled, size) if return_size else scaled

Image = load_image
