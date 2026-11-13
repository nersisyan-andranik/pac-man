*This project has been created as part of the 42 curriculum by anersisy, smusayel.*

# Pac-Man — 42 Curriculum Project

## Description

A multi-level Pac-Man-inspired arcade game built in Python with **pygame-ce**. The player navigates procedurally generated mazes, collects regular and power pellets, avoids or eats ghosts, earns points, and tries to finish ten progressively larger levels before losing all lives or running out of time. The project combines event-driven programming, maze generation, pathfinding, audio, persistent highscores, configurable gameplay and a scene-based UI.

## Play on itch.io

The game is published on itch.io: **[Pac-Man 42 — anersisy](https://anersisy.itch.io/pac-man-42)**. Visit the project page to view the release and download the available build. Platform-specific installation or security prompts may apply to downloaded applications.

## Instructions

### Requirements
- Python **3.10+** (as declared in `pyproject.toml`)
- [`uv`](https://docs.astral.sh/uv/)
- The supplied `packagies/mazegenerator-2.1.0-py3-none-any.whl` wheel (the directory is named `packagies` in this repository)

```bash
make install
make run
# equivalent:
uv sync
uv run python pac-man.py config.json
```

The command-line entry point expects a JSON configuration path when running from source. You can use another file with `make run CONFIG=custom.json`.

Other Makefile commands:

```bash
make lint          # flake8 and mypy
make lint-strict   # flake8 and mypy --strict
make clean         # delete Python/type-check caches outside .venv
make package       # build with pac-man.spec and PyInstaller
```

### Controls

| Screen | Control | Action |
|---|---|---|
| Menu | Space | Start game |
| Menu | Enter | Instructions |
| Menu | Escape | Quit |
| Playing | Arrow keys / WASD | Set Pac-Man direction |
| Playing | P | Pause |
| Playing | Escape | End game |
| Paused | Enter | Resume |
| Paused | Escape | Return to menu |
| Game over | Type / Backspace | Enter or edit player name |
| Game over | Enter | Save score (if name entered), return to menu |
| Game over | Escape | Return without saving |

The in-game **Open Config** button opens the cheat panel. Available actions in `PlayingScene` include invincibility, ghost freeze, double speed, extra life, extra time, skip level and mute. Cheat toggles are intended to persist across level transitions; starting a new game resets them.

## Configuration

The supplied `config.json` contains:

```json
{
  "highscore_filename": "highscore.json",
  "lives": 3,
  "pacgum": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "seed": 0,
  "level_max_time": 90,
  "level": [
    { "width": 20, "height": 15 },
    { "width": 21, "height": 15 },
    { "width": 22, "height": 16 },
    { "width": 23, "height": 16 },
    { "width": 24, "height": 17 },
    { "width": 25, "height": 17 },
    { "width": 26, "height": 18 },
    { "width": 27, "height": 18 },
    { "width": 28, "height": 19 },
    { "width": 29, "height": 19 }
  ]
}

```

The example shows only the first two entries; the actual file defines **10 levels**, ending at **29 × 19**. Width and height specify maze cells, not pixels.

| Key | Supplied config | Purpose |
|---|---|---|
| `highscore_filename` | `highscore.json` | Requested highscore filename |
| `lives` | `3` | Initial lives |
| `pacgum` | `42` | Configured pellet quantity |
| `points_per_pacgum` | `10` | Regular pellet score |
| `points_per_super_pacgum` | `50` | Power pellet score |
| `points_per_ghost` | `200` | Ghost score when edible |
| `seed` | `0` | Requested maze seed |
| `level_max_time` | `90` | Requested level time in seconds |
| `level` | 10 width/height objects | Maze dimensions per level |

**Configuration note:** In the reviewed snapshot, some gameplay values are set directly in `PlayingScene` (including lives, time, pellet sampling and maze seed). Verify that the configuration options you intend to expose are applied consistently. The defaults listed above are from the provided `config.json`.

The parser supports `#`, `//` and `/* ... */` comments outside quoted JSON strings, applies missing-key defaults and raises `ConfigError` for invalid input.

## Highscore

The highscore system is **local JSON persistence**, not an online leaderboard. `GameOverScene` accepts a player name and calls `score/save_score.py` when Enter is pressed. The score file stores objects such as:

```json
[{"name": "PLAYER", "score": 1200}]
```

The save function keeps **one record per player name** (case-insensitive comparison) and replaces a previous result only when the new score is higher. `score/load_top_scores.py` sorts saved results in descending order and formats the top entries for the menu (default limit 10). Missing or invalid score files are treated as empty. This design is simple, readable, easy to debug and requires no database or network connection.

**Implementation note:** `MenuScene` and `GameOverScene` use the `HIGHSCORE_PATH` constant, not `game.highscore_filename`, so changing the filename in config may not redirect these operations.

## Maze Generation

`maze_adapter.py` wraps the assigned **A-Maze-ing / `mazegenerator`** package, imported as `MazeGenerator`. The package is installed from the wheel stored in `packagies/` through `pyproject.toml`.

`generate_maze(width, height, seed, entry, exit_)` invokes `MazeGenerator(size=(width, height), perfect=False, entry_cell=..., exit_cell=..., seed=...)`. It checks the returned dimensions and wall values, then converts the result into a local `Maze` dataclass containing dimensions, wall cells, entry/exit and shortest-path metadata. Each cell uses a four-bit wall mask: **NORTH=1, EAST=2, SOUTH=4, WEST=8**. `Maze.has_wall()` and `Maze.can_move()` expose wall checks; `to_wall_grid()` can expand the cell representation into a wall/passage grid.

`PlayingScene.load_level()` requests a new maze for each level, while `generate_points()` selects eligible cells for pellets and reserves the corners for power pellets. Pac-Man starts near the center, chosen from cells with sufficient accessible neighbors. Ghost pathfinding and rendering use the same maze cell data.

## Implementation

- **Game loop:** `Game.run()` polls Pygame events, updates the active scene using delta time and draws a new frame.
- **Scene lifecycle:** each scene derives from `scenes/base.py` and handles input, update and rendering responsibilities; `Game.change_scene()` selects the active scene.
- **Player movement:** directional movement checks wall bitmasks before changing grid coordinates; movement is time-interval based rather than one cell per rendered frame.
- **Ghosts:** `PlayingScene` implements four strategies (`blinky`, `pinky`, `inky`, `clyde`), a breadth-first path search, collision checks and escape behavior while edible.
- **Progression:** pellets and power pellets increase the score; clearing a level or using the skip action calls `complete_level()`, which advances the level or opens Game Over after the last level.
- **Difficulty:** `update_movement_speed()` changes Pac-Man and ghost movement intervals by level and reapplies the double-speed cheat when enabled.
- **Audio:** `AudioManager` handles introduction, background ghost states, effects, mute and pause/resume; sound files live in `assets/sounds/`.
- **Rendering:** drawing code lives in `display/`, separate from the main game controller and scene state.
- **Error handling:** `errors.py` defines project-specific exceptions; the entry point reports configuration, maze and runtime errors.

## General Software Architecture

The diagram below follows the **actual module imports and ownership in the supplied ZIP**. It does not imply that `PlayingScene` directly imports score modules.

```text
pac-man.py (entry point)
  |-- json_parser.py --> config.json
  |     `-- constants.py / errors.py
  `-- Game (game.py)
        |-- AudioManager (audio_manager.py) --> assets/sounds/
        |-- active Scene (scenes/base.py)
        |     |-- MenuScene (scenes/menu.py)
        |     |     |-- score/load_top_scores.py --> highscore.json
        |     |     `-- display/draw_menu.py
        |     |-- InstructionsScene (scenes/instructions.py)
        |     |     `-- display/draw_instraction.py
        |     |-- PlayingScene (scenes/playing.py)
        |     |     |-- maze_adapter.py --> mazegenerator wheel
        |     |     |-- display/draw_game.py
        |     |     `-- AudioManager via Game
        |     |-- PausedScene (scenes/paused.py)
        |     |     `-- display/draw_paused.py
        |     `-- GameOverScene (scenes/game_over.py)
        |           |-- score/save_score.py --> highscore.json
        |           `-- display/draw_game_over.py
        |-- constants.py (shared settings/enums)
        `-- pygame display, clock and event loop

Supporting modules:
  display/draw_cheat_mode.py (cheat overlay rendering)
  display/utils.py           (drawing and maze sizing helpers)
  paths.py                   (asset path helper)
  pac-man.spec               (PyInstaller specification)
  .github/workflows/build.yml (cross-platform build workflow)
```

The core design is a **controller plus scenes**: `Game` owns global state and services, scenes manage screen-specific behavior, `maze_adapter.py` isolates the external generator, `display/` draws, and `score/` persists records.

## Project Management

The Pac-Man project was developed by two students as part of the 42 curriculum, following a collaborative and incremental development approach.

### Team Organization

The project was developed collaboratively by:

- **anersisy** — Game logic, gameplay mechanics, ghost behavior, and technical implementation.
- **smusayel** — User interface, visual components, testing, and documentation.

Both team members participated in technical discussions, debugging, code reviews, and integration.

### Development Workflow

The development process was organized into several stages:

1. **Planning and Requirements Analysis:** Reviewing requirements, identifying challenges, and defining features.
2. **Architecture and Setup:** Organizing the Python project, configuring Pygame, and implementing scene management.
3. **Core Gameplay:** Integrating maze generation, Pac-Man movement, scoring, and ghost behavior.
4. **Additional Features:** Implementing audio, highscores, cheat mode, and level progression.
5. **Testing and Debugging:** Testing gameplay, fixing bugs, and running Flake8 and Mypy checks.
6. **Packaging and Documentation:** Preparing the game for itch.io and documenting the project.


## Resources

- [Python documentation](https://docs.python.org/3/)
- [pygame-ce documentation](https://pyga.me/docs/)
- [uv documentation](https://docs.astral.sh/uv/)
- [PyInstaller documentation](https://pyinstaller.org/en/stable/)
- [Python `json` documentation](https://docs.python.org/3/library/json.html)
- [Python `collections.deque` documentation](https://docs.python.org/3/library/collections.html#collections.deque) (useful for BFS)
- Assigned `mazegenerator` wheel in `packagies/` and its API as used by `maze_adapter.py`

### AI use disclosure

AI assistance was used during development discussions for **Python typing and lint fixes**, explaining Pygame and game architecture concepts, and drafting/reviewing **README and project-management documentation**. Any other AI-assisted contributions, code generation or testing should be added by the authors after reviewing their actual work. The authors remain responsible for verifying the code, tests and documentation.
