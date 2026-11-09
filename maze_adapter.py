from dataclasses import dataclass
from constants import WEST, SOUTH, EAST, NORTH
from errors import MazeGenerationError


@dataclass
class Maze:
    """Represent a generated maze for use by the game.

    Stores the maze dimensions, cell wall data, entry and exit
    coordinates, and the shortest path. Other game components,
    such as rendering and movement, use this representation.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        cells: 2D list containing the wall bitmask for each cell.
            Each cell uses NORTH=1, EAST=2, SOUTH=4, WEST=8.
        entry: Coordinates (x, y) of the entry cell.
        exit: Coordinates (x, y) of the exit cell.
        shortest_path: String describing the shortest path from
            entry to exit, using direction characters.
    """

    width: int
    height: int
    cells: list[list[int]]
    entry: tuple[int, int]
    exit: tuple[int, int]
    shortest_path: str

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        """Check whether a cell has a wall in a given direction.

        Args:
            x: Horizontal coordinate of the cell.
            y: Vertical coordinate of the cell.
            direction: Direction bitmask (NORTH, EAST, SOUTH, or WEST).

        Returns:
            True if the specified wall exists, otherwise False.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return bool(self.cells[y][x] & direction)

    def can_move(self, x: int, y: int, direction: int) -> bool:
        """Check whether movement out of a cell is not blocked by a wall.

        Args:
            x: Horizontal coordinate of the current cell.
            y: Vertical coordinate of the current cell.
            direction: Direction of the intended movement.

        Returns:
            True if there is no wall in the specified direction,
            otherwise False.
        """
        if direction not in (NORTH, EAST, SOUTH, WEST):
            return False
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        dx, dy = {
            NORTH: (0, -1), EAST: (1, 0),
            SOUTH: (0, 1), WEST: (-1, 0),
        }[direction]
        nx, ny = x + dx, y + dy
        return (
            0 <= nx < self.width
            and 0 <= ny < self.height
            and not self.has_wall(x, y, direction)
            and self.cells[ny][nx] != 15
        )


def generate_maze(
    width: int,
    height: int,
    seed: int = 0,
    entry: tuple[int, int] = (0, 0),
    exit_: tuple[int, int] = (-1, -1),
) -> Maze:
    """Generate a maze and convert it to the game's Maze representation.

    Uses the external MazeGenerator package with perfect=False to
    generate a maze with loops and without dead ends, according to
    the generator's behavior.

    Args:
        width: Number of columns in the maze. Must be positive.
        height: Number of rows in the maze. Must be positive.
        seed: Random seed used to generate a reproducible maze.
        entry: Requested entry coordinates (x, y).
        exit_: Requested exit coordinates (x, y). The default
            (-1, -1) is interpreted by the generator.

    Returns:
        A Maze object containing the dimensions, cell wall data,
        actual entry and exit coordinates, and shortest path.

    Raises:
        MazeGenerationError: If the dimensions are invalid, maze
            generation fails, or the generated maze has an
            unexpected shape.
    """
    if width <= 0 or height <= 0:
        raise MazeGenerationError(
            f"invalid maze size {width}x{height}: both must be positive"
        )

    try:
        from mazegenerator import MazeGenerator

        raw = MazeGenerator(
            size=(width, height),
            perfect=False,
            entry_cell=entry,
            exit_cell=exit_,
            seed=seed,
        )
    except ImportError as e:
        raise MazeGenerationError(
            "the assigned 'mazegenerator' package is not installed; "
            "run 'make install' from the project directory"
        ) from e
    except Exception as e:
        raise MazeGenerationError(
            "maze generation failed for size "
            f"{width}x{height}, seed={seed}: {e}"
        ) from e

    try:
        cells = raw.maze
        entry_cell = raw.maze_entry
        exit_cell = raw.maze_exit
        shortest_path = raw.shortest_path
    except Exception as e:
        raise MazeGenerationError(
            f"maze generator returned incomplete data for size "
            f"{width}x{height}: {e}"
        ) from e
    if not isinstance(cells, list):
        shape = f"invalid {type(cells).__name__} result"
    elif len(cells) != height or any(
        not isinstance(row, list) or len(row) != width for row in cells
    ):
        first_row_valid = bool(cells) and isinstance(cells[0], list)
        actual_width = len(cells[0]) if first_row_valid else 0
        shape = f"{len(cells)}x{actual_width}"
    else:
        shape = ""
    if shape:
        raise MazeGenerationError(
            f"generator returned an unexpected maze shape ({shape}); "
            f"expected {width}x{height}"
        )
    if any(
        isinstance(cell, bool)
        or not isinstance(cell, int)
        or not 0 <= cell <= 15
        for row in cells for cell in row
    ):
        raise MazeGenerationError("generator returned invalid wall bitmasks")

    if shortest_path is False:
        shortest_path = ""
    if not isinstance(shortest_path, str):
        raise MazeGenerationError(
            "generator returned an invalid shortest path"
        )

    return Maze(
        width=width,
        height=height,
        cells=cells,
        entry=entry_cell,
        exit=exit_cell,
        shortest_path=shortest_path,
    )


def to_wall_grid(maze: Maze) -> list[list[int]]:
    """Convert maze cells into an expanded grid of walls and passages.

    Each original cell is represented by a position at an odd row
    and odd column in the expanded grid. Adjacent positions are
    opened when the corresponding cell wall is absent.

    The output grid has dimensions (2 * height + 1) by
    (2 * width + 1).

    Args:
        maze: Maze object to convert.

    Returns:
        A 2D list where 1 represents a wall and 0 represents
        an open passage or cell.
    """
    gw, gh = maze.width * 2 + 1, maze.height * 2 + 1
    grid = [[1] * gw for _ in range(gh)]

    for y in range(maze.height):
        for x in range(maze.width):
            gx, gy = x * 2 + 1, y * 2 + 1
            if maze.cells[y][x] == 15:
                continue
            grid[gy][gx] = 0

            if not maze.has_wall(x, y, NORTH):
                grid[gy - 1][gx] = 0

            if not maze.has_wall(x, y, SOUTH):
                grid[gy + 1][gx] = 0

            if not maze.has_wall(x, y, EAST):
                grid[gy][gx + 1] = 0

            if not maze.has_wall(x, y, WEST):
                grid[gy][gx - 1] = 0

    return grid
