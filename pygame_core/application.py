import sys
import os
import pygame
from pygame import mixer
from pygame_core.mouse import Mouse


class Application():
    def __init__(self, size: tuple[int, int], title: str, fps: int, mouse=None) -> None:
        self._is_running = False
        self._fps = fps
        self._is_in_debug_mode = False
        self.mouse_pos = (0, 0)
        self.mouse = mouse if mouse is not None else Mouse()

        self.init_pygame()
        self.set_title(title)
        self.fetch_screen_dimensions(size)
        self.full_screen()
        self.center_window()
        self.clock = pygame.time.Clock()

    @staticmethod
    def init_pygame() -> None:
        pygame.init()
        mixer.init()

    @staticmethod
    def center_window():
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def fetch_screen_dimensions(self, size: tuple[int, int]):
        self.info_object = pygame.display.Info()
        self.full_screen_size = self.full_screen_width, self.full_screen_height = self.info_object.current_w, self.info_object.current_h
        self.minimized_size = self.minimized_width, self.minimized_height = size
        self.scale = self.full_screen_width / self.minimized_width, self.full_screen_height / self.minimized_height

    @staticmethod
    def get_title() -> str:
        return pygame.display.get_caption()[0]

    @staticmethod
    def set_title(title):
        pygame.display.set_caption(title)

    def minimize(self):
        self.set_size(self.minimized_size)
        self.window = pygame.display.set_mode(self.size)

    def full_screen(self):
        self.set_size(self.minimized_size)
        self.window = pygame.display.set_mode(self.size, pygame.FULLSCREEN | pygame.SCALED)

    def set_size(self, size: tuple) -> None:
        self.size = self.width, self.height = size

    def run(self) -> None:
        self._is_running = True

        while self._is_running:
            self.clock.tick(self._fps)
            self._listen_inputs()
            self._handle_events()
            self.update()
            self.draw()
            self.draw_mouse()
            self.draw_debug()
            pygame.display.update()

    def _listen_inputs(self) -> None:
        if self.mouse:
            self.mouse.update()
        self.keys = pygame.key.get_pressed()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            self._handle_core_event(event)
            self._handle_event(event)

    def _handle_core_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_exit()
            elif event.key == pygame.K_F1:
                self._is_in_debug_mode = not self._is_in_debug_mode
            elif event.key == pygame.K_F11:
                self.full_screen() if self.size == self.minimized_size else self.minimize()
            elif event.type == pygame.QUIT:
                self.on_exit()

    # region Override these methods in subclasses (Abstract Methods)

    def _handle_event(self, event: pygame.event.Event) -> None:
        """Override this method in subclasses to handle events. This method is called once per event."""

        pass

    def update(self) -> None:
        """Override this method in subclasses to update the game state. This method is called once per frame."""

        pass

    def draw(self) -> None:
        """Override this method in subclasses to draw the game state. This method is called once per frame."""

        pass

    def draw_mouse(self) -> None:
        if self.mouse:
            self.mouse.draw(self.window)

    def draw_debug(self) -> None:
        """Override this method in subclasses to draw debug information. This method is called once per frame when debug mode is enabled."""

        pass

    # endregion

    def on_exit(self) -> None:
        self.exit()

    def exit(self) -> None:
        self._is_running = False
        pygame.quit()
        sys.exit()