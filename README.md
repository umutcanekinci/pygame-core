# pygame_core

Shared pygame utilities used across personal game projects (2048-idle-evolution, terraria, tower-defense).

## Installation

From the `PycharmProjects` root, install once in editable mode:

```bash
pip install -e ./pygame_core
```

Editable mode means any change you make inside `pygame_core/` is immediately available in all games — no reinstall needed.

## Modules

### `pygame_core.color`
Common color constants as RGB tuples.

```python
from pygame_core.color import *

# Available: Black, White, Red, Lime, Blue, Yellow, Cyan, Magenta,
#            Silver, Gray, Maroon, Olive, Green, Purple, Teal, Navy, CustomBlue
```

---

### `pygame_core.path`
Path helper classes that resolve asset paths relative to the game's working directory.

```python
from pygame_core.path import ImagePath, FontPath, SoundPath, FilePath

img   = ImagePath("player")           # → <cwd>/images/player.png
img   = ImagePath("hero", "sprites")  # → <cwd>/images/sprites/hero.png
font  = FontPath("comic")             # → <cwd>/fonts/comic.ttf
sound = SoundPath("jump")             # → <cwd>/sounds/jump.ogg
```

All classes inherit from `str`, so they can be passed directly to `pygame.image.load`, `pygame.font.Font`, etc.

---

### `pygame_core.image`
Image loading with optional scaling.

```python
from pygame_core.image import GetImage  # or: Image (same function, alias)

surface = GetImage(ImagePath("player"))               # original size
surface = GetImage(ImagePath("player"), [64, 64])     # scaled to 64×64
surface = GetImage(ImagePath("player"), [0, 32])      # keeps original width, scales height to 32
surface, size = GetImage(ImagePath("player"), [64, 64], ReturnSize=True)
```

`Image` is exported as an alias of `GetImage` for compatibility with older project code.

---

### `pygame_core.input_box`
A simple text input field component.

```python
from pygame_core.input_box import InputBox

box = InputBox(x=100, y=200, w=200, h=40, text="default")

# In your event loop:
box.HandleEvents(event, mouse_pos)
box.update()

# In your draw call:
box.Draw(screen)

# Read the current value:
print(box.text)
```

---

### `pygame_core.database`
Thin SQLite wrapper that stores `.db` files in a `databases/` folder next to the game.

```python
from pygame_core.database import Database

db = Database("savefile")
db.Connect()
db.Execute("CREATE TABLE IF NOT EXISTS scores (name TEXT, value INTEGER)")
db.Commit()
db.Disconnect()
```

---

## Project structure

```
PycharmProjects/
├── pygame_core/                  ← this package
│   ├── pyproject.toml
│   ├── README.md
│   ├── __init__.py
│   ├── color.py
│   ├── path.py
│   ├── image.py
│   ├── input_box.py
│   └── database.py
├── 2048-idle-evolution/
├── terraria/
└── tower-defense/
```

Each game's local files (e.g. `scripts/default/color.py`) are thin wrappers that re-export from this package, so existing internal imports inside each game are unchanged.

## Adding a new module

1. Create `pygame_core/<module>.py`
2. Import it where needed: `from pygame_core.<module> import ...`
3. No reinstall required (editable install picks it up automatically)
