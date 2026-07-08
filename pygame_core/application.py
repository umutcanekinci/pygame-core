from __future__ import annotations

import sys
import os
import pygame
from pygame import mixer
from pygame_core.mouse import Mouse

# Common desktop resolutions offered by a windowed-mode resolution picker
# (available_windowed_resolutions() filters this down to what fits the
# screen). 16:9/16:10 only -- covers the vast majority of desktop monitors.
COMMON_RESOLUTIONS: tuple[tuple[int, int], ...] = (
    (1024, 576), (1152, 648), (1280, 720), (1280, 800), (1366, 768),
    (1440, 900), (1536, 864), (1600, 900), (1680, 1050), (1920, 1080),
    (1920, 1200), (2560, 1440), (3200, 1800), (3840, 2160),
)


class Application:
    # Cycle order for F11 / cycle_window_mode(): exclusive fullscreen (real
    # display mode switch) -> borderless fullscreen (screen-filling window,
    # no mode switch -- avoids the flash/flicker of a mode switch and plays
    # nicer with Windows DPI/GPU scaling) -> bordered windowed.
    WINDOW_MODES: tuple[str, ...] = ("fullscreen", "borderless", "windowed")

    def __init__(self, size: tuple[int, int], title: str, fps: int, mouse=None) -> None:
        self._is_running = False
        self._fps = fps
        self._is_in_debug_mode = False
        self._window_mode = "windowed"  # overwritten below by full_screen()
        self._windowed_resolution_override: tuple[int, int] | None = None
        self.size: tuple[int, int] = size
        self.mouse_pos = (0, 0)
        self.mouse = mouse if mouse is not None else Mouse()

        self.init_pygame()
        self.set_title(title)
        self.fetch_screen_dimensions(size)
        # Fixed logical render target: every draw call in the game targets
        # this, at the authored design resolution, regardless of what size
        # the real OS window actually is. _present() scales it onto the real
        # window each frame -- this is what lets windowed mode be a genuinely
        # smaller/bordered window instead of forcing the OS window to match
        # the design resolution 1:1.
        self.window = pygame.Surface(self.minimized_size)
        self.full_screen()
        self.window = self.window.convert()  # match the now-established display format
        self.center_window()
        self.clock = pygame.time.Clock()

    @staticmethod
    def init_pygame() -> None:
        Application._set_windows_dpi_aware()
        pygame.init()
        mixer.init()

    @staticmethod
    def _set_windows_dpi_aware() -> None:
        # Without this, Windows treats the process as DPI-unaware and reports
        # a scaled-down virtual desktop size (e.g. 1536x864 on a 1920x1080
        # screen at 125% scaling). Exclusive FULLSCREEN still renders at the
        # real resolution, but windowed mode gets bitmap-stretched by the
        # OS to match -- the window ends up larger than the physical screen
        # and only its (stretched, zoomed-looking) center is visible.
        if sys.platform != "win32":
            return
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
            return
        except (AttributeError, OSError):
            pass
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            return
        except (AttributeError, OSError):
            pass
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass

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
    def set_title(title: str) -> None:
        pygame.display.set_caption(title)

    def minimize(self):
        # A bordered window sized to exactly fill the screen has nowhere to
        # put its title bar/borders -- they get pushed off-screen and it
        # looks identical to FULLSCREEN. _windowed_physical_size() shrinks
        # the real OS window enough to leave room for them; self.window (the
        # logical render target every draw call uses) stays at the full
        # design resolution regardless, and _present() scales it down to fit.
        self.set_size(self.minimized_size)
        self.display_surface = pygame.display.set_mode(self._windowed_physical_size())
        self._sync_mouse_scale()
        self._window_mode = "windowed"

    def full_screen(self):
        self.set_size(self.minimized_size)
        self.display_surface = pygame.display.set_mode(self.full_screen_size, pygame.FULLSCREEN)
        self._sync_mouse_scale()
        self._window_mode = "fullscreen"

    def borderless_full_screen(self):
        # A window sized to exactly the screen with no border/title bar --
        # fills the screen like FULLSCREEN but without an exclusive display
        # mode switch, so no flash/flicker on alt-tab and no interaction
        # with GPU/monitor scaling behavior tied to exclusive mode switches.
        self.set_size(self.minimized_size)
        self.display_surface = pygame.display.set_mode(self.full_screen_size, pygame.NOFRAME)
        self._sync_mouse_scale()
        self._window_mode = "borderless"

    def cycle_window_mode(self, step: int = 1) -> None:
        """Advance through WINDOW_MODES by `step` (wraps around) and apply
        the result. F11 calls this with the default step to cycle
        fullscreen -> borderless -> windowed -> fullscreen ..."""
        methods = {
            "fullscreen": self.full_screen,
            "borderless": self.borderless_full_screen,
            "windowed": self.minimize,
        }
        index = self.WINDOW_MODES.index(self._window_mode)
        new_mode = self.WINDOW_MODES[(index + step) % len(self.WINDOW_MODES)]
        methods[new_mode]()

    @property
    def _is_fullscreen(self) -> bool:
        """True only for exclusive FULLSCREEN -- kept as a read-only alias
        of `_window_mode` for existing callers that only care about the
        fullscreen/not-fullscreen distinction (e.g. windowed_resolution
        picking, which treats borderless the same as windowed)."""
        return self._window_mode == "fullscreen"

    def _windowed_physical_size(self) -> tuple[int, int]:
        if self._windowed_resolution_override is not None:
            return self._windowed_resolution_override
        # Leave headroom for window chrome (title bar/borders) and never
        # upscale past the design resolution -- cap the shrink factor at 1.0.
        margin = 0.8
        fit = min(
            1.0,
            margin * self.full_screen_width / self.minimized_width,
            margin * self.full_screen_height / self.minimized_height,
        )
        return (round(self.minimized_width * fit), round(self.minimized_height * fit))

    def available_windowed_resolutions(self) -> list[tuple[int, int]]:
        """Common resolutions that fit this screen with room to spare for
        window chrome (same margin _windowed_physical_size() uses when there's
        no explicit choice), plus whatever's currently selected so there's
        always at least one entry and the current pick is never dropped."""
        margin = 0.8
        max_width = margin * self.full_screen_width
        max_height = margin * self.full_screen_height
        fitting = {r for r in COMMON_RESOLUTIONS if r[0] <= max_width and r[1] <= max_height}
        fitting.add(self.windowed_resolution)
        return sorted(fitting)

    def _auto_windowed_physical_size(self) -> tuple[int, int]:
        override, self._windowed_resolution_override = self._windowed_resolution_override, None
        try:
            return self._windowed_physical_size()
        finally:
            self._windowed_resolution_override = override

    @property
    def windowed_resolution(self) -> tuple[int, int]:
        """The physical size minimize() will use right now -- either an
        explicit pick from set_windowed_resolution()/cycle_windowed_resolution(),
        or the automatic best-fit size. Useful for a settings label to show
        the current selection even before the player has ever gone windowed."""
        return self._windowed_resolution_override or self._auto_windowed_physical_size()

    def set_windowed_resolution(self, size: tuple[int, int]) -> None:
        """Explicitly choose the physical window size minimize() uses,
        overriding the automatic best-fit calculation, and switch to
        windowed mode showing it -- a "resolution" is inherently a windowed
        concept (fullscreen is always the native monitor resolution), so
        picking one should give immediate visible feedback rather than
        silently applying next time the player happens to press F11."""
        self._windowed_resolution_override = size
        self.minimize()

    def clear_windowed_resolution_override(self) -> None:
        """Drop any explicit pick, reverting windowed_resolution to the
        automatic best-fit calculation. Doesn't switch mode or resize the
        window itself -- pair with minimize() (or leave it for the next
        minimize()/F11 press) if the change should be visible immediately."""
        self._windowed_resolution_override = None

    def cycle_windowed_resolution(self, step: int = 1) -> tuple[int, int]:
        """Advance through available_windowed_resolutions() by `step`
        (wraps around) and apply the result. Returns the newly selected size
        -- the return value is what a resolution-cycler label should show."""
        options = self.available_windowed_resolutions()
        current = self.windowed_resolution
        index = options.index(current) if current in options else 0
        new_size = options[(index + step) % len(options)]
        self.set_windowed_resolution(new_size)
        return new_size

    def _sync_mouse_scale(self) -> None:
        if not self.mouse:
            return
        physical_width, physical_height = self.display_surface.get_size()
        self.mouse.scale = (self.window.get_width() / physical_width, self.window.get_height() / physical_height)

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
            if self._is_in_debug_mode:
                self.draw_debug()
            self._present()

    def _present(self) -> None:
        if self.window.get_size() == self.display_surface.get_size():
            self.display_surface.blit(self.window, (0, 0))
        else:
            pygame.transform.scale(self.window, self.display_surface.get_size(), self.display_surface)
        pygame.display.update()

    def _listen_inputs(self) -> None:
        if self.mouse:
            self.mouse.update()
        self.keys = pygame.key.get_pressed()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            self._handle_core_event(event)
            self.handle_event(event)

    def _handle_core_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_exit_request()
            elif event.key == pygame.K_F1:
                self._is_in_debug_mode = not self._is_in_debug_mode
            elif event.key == pygame.K_F11:
                self.cycle_window_mode()
        elif event.type == pygame.QUIT:
            self.on_exit_request()

    # region Override these methods in subclasses (Abstract Methods)

    def handle_event(self, event: pygame.event.Event) -> None:
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

    def on_exit_request(self) -> None:
        self.exit()

    def exit(self) -> None:
        self._is_running = False
        pygame.quit()
        sys.exit()