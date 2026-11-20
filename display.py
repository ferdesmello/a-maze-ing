#!/usr/bin/env python3

from mazegen import NORTH, SOUTH, EAST, WEST


# ANSI colors
RESET = "\033[0m"
WALL_COLOR = "\033[99m"       # Light gray
PATH_COLOR = "\033[1;31m"     # Red
START_COLOR = "\033[1;31m"    # Bright red
EXIT_COLOR = "\033[1;31m"     # Bright red
LOGO_COLOR = "\033[1;33m"     # Yellow

# Direction offsets: (dx, dy)
DIRECTIONS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}

OPPOSITE = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
}

PATH_GLYPHS = {
    frozenset(("E", "W")): "─",
    frozenset(("N", "S")): "╎",
    frozenset(("N", "E")): "└",
    frozenset(("N", "W")): "┘",
    frozenset(("S", "E")): "┌",
    frozenset(("S", "W")): "┐",
}

# Box-drawing lookup table based on presence of
# walls (North, South, East, West)
BOX_DRAWING = {
    # 4-way & 3-way junctions
    (True,  True,  True,  True):  "┼",
    (True,  True,  True,  False): "├",
    (True,  True,  False, True):  "┤",
    (True,  False, True,  True):  "┴",
    (False, True,  True,  True):  "┬",

    # 2-way corners & straight lines
    (True,  True,  False, False): "│",
    (False, False, True,  True):  "─",
    (False, True,  True,  False): "┌",
    (False, True,  False, True):  "┐",
    (True,  False, True,  False): "└",
    (True,  False, False, True):  "┘",

    # Terminating vertical wall stubs
    # set to space to prevent floating stubs
    (True,  False, False, False): "│",
    (False, True,  False, False): "│",

    # Terminating horizontal wall stubs
    # set to space to prevent floating stubs
    (False, False, True,  False): " ",
    (False, False, False, True):  " ",

    # Fully open space
    (False, False, False, False): " ",
}


def get_path_cells(
        path: list[str],
        start_cell: tuple[int, int]
) -> list[tuple[int, int]]:
    """Return the cells visited by a path of N/S/E/W directions.

    Args:
        path: A list of directions (N, S, E, W).
        start_cell: The starting position (x, y).
    Returns:
        A list of positions (x, y) visited by the path.
    """
    x, y = start_cell
    cells = [(x, y)]

    for direction in path:
        dx, dy = DIRECTIONS[direction]
        x += dx
        y += dy
        cells.append((x, y))

    return cells


def get_path_connections(
    path: list[str],
    start_cell: tuple[int, int],
) -> dict[tuple[int, int], set[str]]:
    """Map each path cell to its incoming and outgoing directions.

    Args:
        path: A list of directions (N, S, E, W).
        start_cell: The starting position (x, y).
    Returns:
        A dictionary mapping each path cell to a set
            of its incoming and outgoing directions.
    """
    x, y = start_cell
    connections: dict[tuple[int, int], set[str]] = {}

    for direction in path:
        current = (x, y)
        dx, dy = DIRECTIONS[direction]
        x += dx
        y += dy
        neighbor = (x, y)

        connections.setdefault(current, set()).add(direction)
        connections.setdefault(neighbor, set()).add(OPPOSITE[direction])

    return connections


def display_maze(
    maze_hex: list[list[int]],
    path: list[str] | None = None,
    wall_color: str = WALL_COLOR,
    start_cell: tuple[int, int] = (0, 0),
    exit_cell: tuple[int, int] | None = None,
    color: bool = True,
    blocked_cells: set[tuple[int, int]] | None = None
) -> None:
    """Display a maze with box-drawing wall connections and path rendering.

    Args:
        maze_hex: A 2D list of integers representing the maze grid.
        path: A list of directions (N, S, E, W)
            representing the path to display.
        wall_color: The color to use for the walls.
        start_cell: The starting position (x, y).
        exit_cell: The exit position (x, y).
        color: Whether to use colors in the output.
        blocked_cells: A set of cells that are blocked.
    """
    height = len(maze_hex)
    width = len(maze_hex[0])

    path_connections: dict[tuple[int, int], set[str]] = {}
    blocked: set[tuple[int, int]] = (
        blocked_cells if blocked_cells is not None else set()
    )

    if path is not None:
        path_connections = get_path_connections(path, start_cell)
        cells = get_path_cells(path, start_cell)
        if exit_cell is None and cells:
            exit_cell = cells[-1]

    def wall(text: str) -> str:
        """Return the text wrapped in wall color if color is enabled."""
        if color:
            return f"{wall_color}{text}{RESET}"
        return text

    def path_fmt(text: str) -> str:
        """Return the text wrapped in path color if color is enabled."""
        if color:
            return f"{PATH_COLOR}{text}{RESET}"
        return text

    def logo_fmt(text: str) -> str:
        """Return the text wrapped in logo color if color is enabled."""
        if color:
            return f"{LOGO_COLOR}{text}{RESET}"
        return text

    def has_wall_north(gx: int, gy: int) -> bool:
        """Check if there is a vertical wall
        above grid point (gx, gy).
        """
        if gy <= 0:
            return False
        if gx < width and (maze_hex[gy - 1][gx] & WEST):
            return True
        if gx > 0 and (maze_hex[gy - 1][gx - 1] & EAST):
            return True
        return False

    def has_wall_south(gx: int, gy: int) -> bool:
        """Check if there is a vertical wall
        below grid point (gx, gy).
        """
        if gy >= height:
            return False
        if gx < width and (maze_hex[gy][gx] & WEST):
            return True
        if gx > 0 and (maze_hex[gy][gx - 1] & EAST):
            return True
        return False

    def has_wall_west(gx: int, gy: int) -> bool:
        """Check if there is a horizontal wall
        to the left of grid point (gx, gy).
        """
        if gx <= 0:
            return False
        # Top exterior line
        if gy == 0:
            return bool(maze_hex[0][gx - 1] & NORTH)
        # Bottom exterior line
        # (check if previous cell actually has a SOUTH wall)
        if gy == height:
            return bool(maze_hex[height - 1][gx - 1] & SOUTH)

        return bool(
            (maze_hex[gy][gx - 1] & NORTH) or
            (maze_hex[gy - 1][gx - 1] & SOUTH)
            )

    def has_wall_east(gx: int, gy: int) -> bool:
        """Check if there is a horizontal wall
        to the right of grid point (gx, gy).
        """
        if gx >= width:
            return False
        # Top exterior line
        if gy == 0:
            return bool(maze_hex[0][gx] & NORTH)
        # Bottom exterior line
        # (check if current cell actually has a SOUTH wall)
        if gy == height:
            return bool(maze_hex[height - 1][gx] & SOUTH)

        return bool(
            (maze_hex[gy][gx] & NORTH) or
            (maze_hex[gy - 1][gx] & SOUTH)
            )

    def get_intersection_glyph(gx: int, gy: int) -> str:
        """Return the appropriate box-drawing glyph
        for the intersection at (gx, gy).
        """
        n = has_wall_north(gx, gy)
        s = has_wall_south(gx, gy)
        e = has_wall_east(gx, gy)
        w = has_wall_west(gx, gy)

        return BOX_DRAWING.get((n, s, e, w), " ")

    def cell_content(x: int, y: int) -> str:
        """Return the content of a cell at (x, y) based on its state.

        Args:
            x: The x-coordinate of the cell.
            y: The y-coordinate of the cell.
        Returns:
            str: The content of the cell.
        """
        position = (x, y)

        if position in blocked:
            return logo_fmt("███")

        if position == start_cell:
            content = " B "
            return f"{START_COLOR}{content}{RESET}" if color else content

        if position == exit_cell:
            content = " X "
            return f"{EXIT_COLOR}{content}{RESET}" if color else content

        if position in path_connections:
            directions = frozenset(path_connections[position])
            glyph = PATH_GLYPHS.get(directions, "•")
            return path_fmt(f" {glyph} ")

        return "   "

    for y in range(height):
        # ----------------------------------------------------
        # 1. Top intersections and horizontal wall row
        top = ""
        for x in range(width):
            top += wall(get_intersection_glyph(x, y))

            if maze_hex[y][x] & NORTH:
                top += wall("───")
            else:
                if "N" in path_connections.get((x, y), set()):
                    top += path_fmt(" ╎ ")
                else:
                    top += "   "

        top += wall(get_intersection_glyph(width, y))
        print(top)

        # ----------------------------------------------------
        # 2. Vertical walls and cell interiors
        middle = ""
        for x in range(width):
            if maze_hex[y][x] & WEST:
                middle += wall("│")
            else:
                if "W" in path_connections.get((x, y), set()):
                    middle += path_fmt("─")
                else:
                    middle += " "

            middle += cell_content(x, y)

        if maze_hex[y][width - 1] & EAST:
            middle += wall("│")
        else:
            if "E" in path_connections.get((width - 1, y), set()):
                middle += path_fmt("─")
            else:
                middle += " "

        print(middle)

    # ----------------------------------------------------
    # 3. Bottom intersections and horizontal walls for final row
    bottom = ""
    for x in range(width):
        bottom += wall(get_intersection_glyph(x, height))
        if maze_hex[height - 1][x] & SOUTH:
            bottom += wall("───")
        else:
            if "S" in path_connections.get((x, height - 1), set()):
                bottom += path_fmt(" ╎ ")
            else:
                bottom += "   "

    bottom += wall(get_intersection_glyph(width, height))
    print(bottom)


if __name__ == "__main__":
    pass
