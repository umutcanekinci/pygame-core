"""Unit tests for Application: the base game-loop class every project's
Game class extends.

Constructs real Application instances against the dummy SDL driver rather
than mocking pygame.display/mixer wholesale -- this is deliberately an
integration-style test of the loop wiring itself. sys.exit and pygame.quit
are monkeypatched wherever exit() is exercised, since calling them for real
would tear down the shared pygame session for every later test in the suite.
"""

import os
import sys

import pygame
import pytest

from pygame_core.application import Application
from pygame_core.mouse import Mouse


class _TrackedApp(Application):
    def __init__(self, **kwargs):
        self.handled_events = []
        self.update_calls = 0
        self.draw_calls = 0
        self.draw_debug_calls = 0
        super().__init__(size=(320, 240), title="Test App", fps=0, **kwargs)

    def handle_event(self, event):
        self.handled_events.append(event)

    def update(self):
        self.update_calls += 1

    def draw(self):
        self.draw_calls += 1

    def draw_debug(self):
        self.draw_debug_calls += 1


@pytest.fixture
def no_real_exit(monkeypatch):
    """Prevent exit()'s real side effects (pygame.quit tears down the shared
    session; sys.exit raises SystemExit) while still letting us observe that
    they were requested."""
    calls = {"pygame_quit": 0, "sys_exit": 0}
    monkeypatch.setattr(pygame, "quit", lambda: calls.__setitem__("pygame_quit", calls["pygame_quit"] + 1))
    monkeypatch.setattr(sys, "exit", lambda: calls.__setitem__("sys_exit", calls["sys_exit"] + 1))
    return calls


# ── construction ───────────────────────────────────────────────────────────


def test_init_stores_basic_attributes():
    app = _TrackedApp()
    assert app.size == app.minimized_size
    assert app._fps == 0
    assert app.mouse_pos == (0, 0)
    assert isinstance(app.mouse, Mouse)
    assert app._is_fullscreen is True  # __init__ ends by calling full_screen()


def test_init_uses_injected_mouse_instead_of_default():
    custom_mouse = Mouse()
    app = _TrackedApp(mouse=custom_mouse)
    assert app.mouse is custom_mouse


def test_init_sets_window_title():
    _TrackedApp()
    assert Application.get_title() == "Test App"


def test_fetch_screen_dimensions_computes_scale_from_full_and_minimized_size():
    app = _TrackedApp()
    expected_scale = (
        app.full_screen_width / app.minimized_width,
        app.full_screen_height / app.minimized_height,
    )
    assert app.scale == expected_scale


def test_center_window_sets_sdl_env_var():
    _TrackedApp()
    assert os.environ["SDL_VIDEO_CENTERED"] == "1"


# ── set_size / minimize / full_screen ──────────────────────────────────


def test_set_size_updates_size_width_height():
    app = _TrackedApp()
    app.set_size((100, 200))
    assert app.size == (100, 200)
    assert app.width == 100
    assert app.height == 200


def test_full_screen_and_minimize_both_resize_to_minimized_size():
    """minimize() and full_screen() intentionally both call
    set_size(self.minimized_size) -- the passed size is the logical/authored
    resolution, and pygame.SCALED has SDL upscale it to fill the real screen
    in fullscreen mode. They differ in the FULLSCREEN|SCALED flag passed to
    set_mode and in `._is_fullscreen`, not in `.size`."""
    app = _TrackedApp()
    app.set_size((999, 999))

    app.minimize()
    assert app.size == app.minimized_size
    assert app._is_fullscreen is False

    app.set_size((999, 999))
    app.full_screen()
    assert app.size == app.minimized_size
    assert app._is_fullscreen is True


# ── _handle_core_event: debug toggle, F11, escape/quit -> exit ──────────


def test_f1_toggles_debug_mode():
    app = _TrackedApp()
    assert app._is_in_debug_mode is False

    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
    assert app._is_in_debug_mode is True

    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
    assert app._is_in_debug_mode is False


def test_f11_calls_minimize_when_currently_fullscreen():
    """__init__ ends by calling full_screen(), so _is_fullscreen is already
    True at construction -- the first F11 press must minimize, not
    re-enter full_screen() (the bug this toggle used to have: checking
    `self.size == self.minimized_size` couldn't tell fullscreen from
    windowed, since both methods set the same `.size`)."""
    app = _TrackedApp()
    assert app._is_fullscreen is True

    calls = []
    app.full_screen = lambda: calls.append("full_screen")
    app.minimize = lambda: calls.append("minimize")

    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11))

    assert calls == ["minimize"]


def test_f11_calls_full_screen_when_currently_windowed():
    app = _TrackedApp()
    app.minimize()
    assert app._is_fullscreen is False

    calls = []
    app.full_screen = lambda: calls.append("full_screen")
    app.minimize = lambda: calls.append("minimize")

    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11))

    assert calls == ["full_screen"]


def test_f11_toggles_back_and_forth_across_repeated_presses():
    app = _TrackedApp()
    assert app._is_fullscreen is True

    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11))
    assert app._is_fullscreen is False

    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11))
    assert app._is_fullscreen is True


def test_escape_key_requests_exit(no_real_exit):
    app = _TrackedApp()
    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))

    assert app._is_running is False
    assert no_real_exit["pygame_quit"] == 1
    assert no_real_exit["sys_exit"] == 1


def test_quit_event_requests_exit(no_real_exit):
    app = _TrackedApp()
    app._handle_core_event(pygame.event.Event(pygame.QUIT))

    assert app._is_running is False


def test_unrelated_key_event_does_not_toggle_debug_or_exit(no_real_exit):
    app = _TrackedApp()
    app._is_running = True

    app._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))

    assert app._is_in_debug_mode is False
    assert app._is_running is True
    assert no_real_exit["sys_exit"] == 0


# ── event dispatch (_handle_events / handle_event) ─────────────────────


def test_handle_events_calls_handle_event_once_per_queued_event(monkeypatch):
    app = _TrackedApp()
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)

    app._handle_events()

    assert app.handled_events == events


def test_base_handle_event_update_draw_are_harmless_no_ops():
    app = Application(size=(320, 240), title="Base", fps=0)
    app.handle_event(pygame.event.Event(pygame.USEREVENT))
    app.update()
    app.draw()  # none of these should raise


# ── draw_mouse ────────────────────────────────────────────────────────


def test_draw_mouse_calls_mouse_draw_with_window():
    calls = []
    app = _TrackedApp()
    app.mouse.draw = lambda window: calls.append(window)

    app.draw_mouse()

    assert calls == [app.window]


def test_draw_mouse_skips_when_mouse_is_falsy():
    app = _TrackedApp(mouse=None)
    app.draw_mouse()  # must not raise with no mouse object


# ── run() loop ──────────────────────────────────────────────────────────


def test_run_calls_update_and_draw_each_frame_until_stopped(monkeypatch):
    monkeypatch.setattr(pygame.event, "get", lambda: [])

    app = _TrackedApp()

    def _stop_after_first_frame():
        app.update_calls += 1
        if app.update_calls >= 3:
            app._is_running = False

    app.update = _stop_after_first_frame
    app.run()

    assert app.update_calls == 3
    assert app.draw_calls == 3


def test_run_calls_draw_debug_only_in_debug_mode(monkeypatch):
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    app = _TrackedApp()
    app._is_in_debug_mode = True

    call_count = {"n": 0}

    def _stop_after_one():
        call_count["n"] += 1
        if call_count["n"] >= 1:
            app._is_running = False

    app.update = _stop_after_one
    app.run()

    assert app.draw_debug_calls == 1


def test_run_does_not_call_draw_debug_when_disabled(monkeypatch):
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    app = _TrackedApp()
    assert app._is_in_debug_mode is False

    def _stop():
        app._is_running = False

    app.update = _stop
    app.run()

    assert app.draw_debug_calls == 0


def test_run_stops_via_a_queued_quit_event(monkeypatch, no_real_exit):
    """The realistic path: run() processes a real QUIT event through
    _handle_events -> _handle_core_event -> on_exit_request -> exit(),
    which flips _is_running so the loop doesn't continue to a next frame."""
    app = _TrackedApp()
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])

    app.run()

    assert app._is_running is False
    assert app.update_calls == 1  # completed the frame it was asked to exit on
    assert no_real_exit["sys_exit"] == 1


# ── exit() ──────────────────────────────────────────────────────────────


def test_exit_stops_the_loop_flag_and_calls_quit_and_sys_exit(no_real_exit):
    app = _TrackedApp()
    app._is_running = True

    app.exit()

    assert app._is_running is False
    assert no_real_exit["pygame_quit"] == 1
    assert no_real_exit["sys_exit"] == 1


def test_on_exit_request_delegates_to_exit(no_real_exit):
    app = _TrackedApp()
    calls = []
    app.exit = lambda: calls.append(1)

    app.on_exit_request()

    assert calls == [1]
