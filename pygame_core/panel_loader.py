from pathlib import Path
from typing import Any

import yaml

from core.guiobject import GuiObject


class PanelLoader:
    """YAML dosyasından panel tanımlarını okuyup PanelManager'a yükler."""

    def __init__(self, panel_manager, window_size: tuple[int, int]):
        self.pm = panel_manager
        self.window_size = window_size

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Panel definition not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}") from e

        if not isinstance(data, dict):
            raise ValueError(f"Top-level YAML must be a mapping in {path}")

        groups = data.get("groups", {}) or {}
        panels = data.get("panels", {}) or {}

        for tab_name, panel_def in panels.items():
            self._load_panel(tab_name, panel_def, groups)

    # ── internals ─────────────────────────────────────────────────────────

    def _load_panel(self, tab: str, panel_def: dict, groups: dict) -> None:
        # Önce extends ile gelen shared object'leri ekle
        for group_name in panel_def.get("extends", []) or []:
            if group_name not in groups:
                raise KeyError(
                    f"Group '{group_name}' referenced by panel '{tab}' not defined"
                )
            for obj_name, obj_def in groups[group_name].items():
                self._add_object(tab, obj_name, obj_def)

        # Sonra panel'e özgü object'leri ekle (aynı isim varsa override eder)
        for obj_name, obj_def in (panel_def.get("objects", {}) or {}).items():
            self._add_object(tab, obj_name, obj_def)

    def _add_object(self, tab: str, name: str, obj_def: dict) -> None:
        position  = self._resolve_position(obj_def["position"])
        size      = self._resolve_size(obj_def["size"])
        asset     = obj_def["asset"]
        hover     = obj_def.get("hover")
        extension = obj_def.get("extension")

        # GuiObject sinyatürünün opsiyonel parametrelerine göre çağrı yap
        if extension is not None:
            gui = GuiObject(self.window_size, position, size, asset, hover, extension)
        elif hover is not None:
            gui = GuiObject(self.window_size, position, size, asset, hover)
        else:
            gui = GuiObject(self.window_size, position, size, asset)

        self.pm.add_object(tab, name, gui)

    def _resolve_position(self, pos: Any) -> tuple:
        if not isinstance(pos, list) or len(pos) != 2:
            raise ValueError(f"position must be [x, y], got {pos!r}")
        x, y = pos
        # "CENTER" string'i mevcut konvansiyonla uyumlu
        return (x, y)

    def _resolve_size(self, size: Any) -> tuple:
        if size == "WINDOW":
            return self.window_size
        if isinstance(size, list) and len(size) == 2:
            return tuple(size)
        raise ValueError(f"size must be [w, h] or 'WINDOW', got {size!r}")