import yaml
from pathlib import Path
from pygame_core.panel_loader import PanelLoader


class PanelLoaderExt(PanelLoader):
    """PanelLoader extended with object-level template inheritance.

    Adds an ``object_templates`` top-level section to the YAML.  Any object
    (in groups or panels) can write ``extends: <template_name>`` and its
    properties will be merged on top of the template — object keys always win.

    Example YAML
    ------------
    object_templates:
      menu_btn:
        size: [960, 96]
        nine_slice: 8

    panels:
      main_menu:
        objects:
          play:
            extends: menu_btn        # inherits size + nine_slice
            position: [CENTER, 300]  # own keys override / extend the template
            asset: btn_play
            hover: btn_play_hover
    """

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Panel definition not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        templates = data.pop("object_templates", {}) or {}
        if templates:
            self._resolve_extends(data, templates)

        groups = data.get("groups", {}) or {}
        for tab, panel_def in (data.get("panels", {}) or {}).items():
            self._load_panel(tab, panel_def, groups)

    # ── private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_extends(data: dict, templates: dict) -> None:
        for group_def in (data.get("groups", {}) or {}).values():
            PanelLoaderExt._apply_templates(group_def, templates)

        for panel_def in (data.get("panels", {}) or {}).values():
            PanelLoaderExt._apply_templates(
                (panel_def.get("objects") or {}), templates)

    @staticmethod
    def _apply_templates(objects: dict, templates: dict) -> None:
        for name, obj_def in objects.items():
            base_name = obj_def.get("extends")
            if base_name is None:
                continue
            if base_name not in templates:
                raise KeyError(
                    f"Object '{name}' extends unknown template '{base_name}'. "
                    f"Available: {list(templates)}"
                )
            merged = {**templates[base_name], **obj_def}
            del merged["extends"]
            objects[name] = merged