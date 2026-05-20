"""Generic widget factories for PanelLoader.

Each `make_*_factory(assets)` returns a callable `(cfg, parent) -> object` that
PanelLoader invokes for entries with the matching `type:` key. Projects that
need project-specific factories (e.g. menus, buttons) define their own and
register them alongside these.
"""
import pygame

from pygame_core.font import load_font
from pygame_core.sprite_sheet import SpriteSheet
from pygame_core.ui_widgets.text_object import TextObject
from pygame_core.unity.animated_sprite import AnimatedSprite
from pygame_core.unity.components.transform import Transform
from pygame_core.unity.state_object import StateObject, HoverableStateObject


def make_factory(assets):
    def make_gui_object(cfg: dict, parent: Transform) -> StateObject:
        pos          = cfg["position"]
        size         = tuple(cfg["size"]) if cfg["size"] != "WINDOW" else parent
        asset        = cfg.get("asset")
        hover        = cfg.get("hover")
        extra_states = cfg.get("states", {})
        nine_slice   = cfg.get("nine_slice", 0)
        color        = cfg.get("color")

        if color is not None and asset is None:
            obj = StateObject(parent=parent, pos=pos, size=size, image_path=None)
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill(tuple(color))
            obj.images[None] = surf
            obj.set_state(None)
            return obj

        if hover is not None or extra_states:
            obj = HoverableStateObject(parent=parent, pos=pos, size=size, image_path=asset, hover_image_path=hover, nine_slice=nine_slice)
            for state_key, state_cfg in extra_states.items():
                state_asset = assets.image_path(state_cfg["asset"]) if isinstance(state_cfg["asset"], str) else state_cfg["asset"]
                state_hover = assets.image_path(state_cfg["hover"]) if isinstance(state_cfg.get("hover"), str) else state_cfg.get("hover")
                obj.add_state(state_key, state_asset, state_hover)
            return obj
        return StateObject(parent=parent, pos=pos, size=size, image_path=asset, nine_slice=nine_slice)
    return make_gui_object


def make_animated_factory(assets):
    def make_animated_object(cfg: dict, parent: Transform) -> AnimatedSprite:
        pos         = cfg["position"]
        size        = tuple(cfg["size"]) if cfg.get("size") not in (None, "WINDOW") else (0, 0)
        sheet_path  = cfg["asset"]  # pre-resolved to ImagePath by PanelLoader
        frame_count = cfg.get("frame_count", 1)
        fps         = cfg.get("fps", 12.0)
        loop        = cfg.get("loop", True)
        horizontal  = cfg.get("horizontal", True)

        frames = SpriteSheet.from_path(sheet_path).strip(frame_count, horizontal=horizontal)
        return AnimatedSprite(parent=parent, pos=pos, size=size, frames=frames,
                              fps=fps, loop=loop)
    return make_animated_object


def make_text_factory(assets):
    def make_text_object(cfg: dict, parent: Transform) -> TextObject:
        return TextObject(
            parent,
            cfg["position"],
            cfg["text"],
            load_font(cfg, assets),
            cfg.get("color", [255, 255, 255]),
            cfg.get("background_color"),
        )
    return make_text_object
