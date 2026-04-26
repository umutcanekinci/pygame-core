# pygame_core/asset_path.py
from pathlib import Path
from typing import Union


class AssetPath:
    """Game asset path — string-compatible ama type-safe."""

    def __init__(self, name: str, folder: str = "", extension: str = "png",
                 base: str = "assets"):
        self.name = name
        self.folder = folder
        self.extension = extension.lstrip(".")
        self.base = base

    @property
    def full_path(self) -> str:
        parts = [self.base]
        if self.folder:
            parts.append(self.folder)
        return f"{'/'.join(parts)}/{self.name}.{self.extension}"

    def __str__(self) -> str:
        return self.full_path

    def __fspath__(self) -> str:
        # os.PathLike protokolü — pygame.image.load(path) bunu kabul eder
        return self.full_path

    def __repr__(self) -> str:
        return f"AssetPath({self.full_path!r})"


class ImagePath(AssetPath):
    def __init__(self, name: str, folder: str = "", extension: str = "png"):
        super().__init__(name, folder, extension, base="assets/images")


class FontPath(AssetPath):
    def __init__(self, name: str, folder: str = "", extension: str = "ttf"):
        super().__init__(name, folder, extension, base="assets/fonts")


class SoundPath(AssetPath):
    def __init__(self, name: str, folder: str = "", extension: str = "ogg"):
        super().__init__(name, folder, extension, base="assets/sounds")