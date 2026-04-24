#-# Importing Packages #-#
import pygame
from pygame_core.path import *

#-# Image Loading Function #-#
def load_image(path: ImagePath, size=[0, 0], return_size=False):

	if type(size) == tuple:
		size = list(size)

	if size == [0, 0] and return_size == False:
		return pygame.image.load(path).convert_alpha()

	img = pygame.image.load(path).convert_alpha()

	if size[0] == 0: size[0] = img.get_width()
	if size[1] == 0: size[1] = img.get_height()
	if size[0] == 1/3: size[0] = img.get_width()//5
	if size[1] == 1/3: size[1] = img.get_height()//5

	if return_size:
		return [pygame.transform.scale(pygame.image.load(path).convert_alpha(), size), size]

	return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

Image = load_image
