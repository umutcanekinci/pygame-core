from pip._internal.resolution.resolvelib import factory

from pygame_core.asset_manager import AssetManager
from pathlib import Path
from typing import Any, Callable
import yaml

# Factory imzası: config dict + window_size → object
ObjectFactory = Callable[[dict, tuple[int, int]], Any]

class PanelLoader:
    """YAML dosyasından panel tanımlarını okuyup PanelManager'a yükler."""

    def __init__(self, panel_manager, window_size: tuple[int, int], asset_manager: AssetManager):
        self.pm = panel_manager
        self.window_size = window_size
        self.assets = asset_manager
        self._factories: dict[str, ObjectFactory] = {}
        self._default_type: str | None = None

    def register(self, type_name: str, factory: ObjectFactory, *, default: bool = False) -> None:
        self._factories[type_name] = factory
        if default:
            self._default_type = type_name

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Panel definition not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        groups = data.get("groups", {}) or {}
        for tab, panel_def in (data.get("panels", {}) or {}).items():
            self._load_panel(tab, panel_def, groups)

    def _load_panel(self, tab: str, panel_def: dict, groups: dict) -> None:
        for group_name in panel_def.get("extends", []) or []:
            for obj_name, obj_def in groups[group_name].items():
                self._add_object(tab, obj_name, obj_def)
        for obj_name, obj_def in (panel_def.get("objects", {}) or {}).items():
            self._add_object(tab, obj_name, obj_def)

    def _add_object(self, tab: str, name: str, obj_def: dict) -> None:
        type_name = obj_def.get("type", self._default_type)
        if type_name is None:
            raise ValueError(f"Object '{name}' has no type and no default registered")
        if type_name not in self._factories:
            raise KeyError(f"No factory for type '{type_name}'. Registered: {list(self._factories)}")

        if "asset" in obj_def:
            obj_def["asset"] = self.assets.image_path(obj_def["asset"])
        if "hover" in obj_def:
            obj_def["hover"] = self.assets.image_path(obj_def["hover"])

        factory = self._factories[type_name]
        obj = factory(obj_def, self.window_size)
        self.pm.add_object(tab, name, obj)

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