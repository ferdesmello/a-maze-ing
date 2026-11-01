#!/usr/bin/env python3

from mazegen import NORTH, SOUTH, EAST, WEST


# ANSI colors
RESET = "\033[0m"
WALL_COLOR = "\033[99m"       # Light gray
PATH_COLOR = "\033[42m"       # Green background
START_COLOR = "\033[1;31m"    # Bright red
EXIT_COLOR = "\033[1;31m"     # Bright red


# Direction offsets: (dx, dy)
DIRECTIONS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}


def get_path_cells(path: list[str],
                   start: tuple[int, int]) -> list[tuple[int, int]]:
    """Return the cells visited by a path of N/S/E/W directions."""

    x, y = start
    cells = [(x, y)]

    for direction in path:
        dx, dy = DIRECTIONS[direction]
        x += dx
        y += dy
        cells.append((x, y))

    return cells


def display_maze(
    maze_hex: list[list[int]],
    path: list[str] | None = None,
    start: tuple[int, int] = (0, 0),
    color: bool = True,
) -> None:
    """Display a maze, optionally highlighting a path."""

    height = len(maze_hex)
    width = len(maze_hex[0])

    path_cells = set()
    exit_cell = None

    if path is not None:
        cells = get_path_cells(path, start)
        path_cells = set(cells)
        exit_cell = cells[-1]

    def wall(text: str) -> str:
        if color:
            return f"{WALL_COLOR}{text}{RESET}"
        return text

    def cell_content(x: int, y: int) -> str:
        """Return the three-character interior of a cell."""

        position = (x, y)

        if position == start and path is not None:
            content = " S "
            return f"{START_COLOR}{content}{RESET}" if color else content

        if position == exit_cell and path is not None:
            content = " E "
            return f"{EXIT_COLOR}{content}{RESET}" if color else content

        if position in path_cells and color:
            return f"{PATH_COLOR}   {RESET}"

        if position in path_cells:
            return " . "

        return "   "

    for y in range(height):
        # North walls.
        top = wall("┼")

        for x in range(width):
            if maze_hex[y][x] & NORTH:
                top += wall("───")
            else:
                top += "   "

            top += wall("┼")

        print(top)

        # West walls and cell interiors.
        middle = ""

        for x in range(width):
            if maze_hex[y][x] & WEST:
                middle += wall("│")
            else:
                middle += " "

            middle += cell_content(x, y)

        # East wall of the final cell.
        if maze_hex[y][width - 1] & EAST:
            middle += wall("│")
        else:
            middle += " "

        print(middle)

    # South walls of the final row.
    bottom = wall("┼")

    for x in range(width):
        if maze_hex[height - 1][x] & SOUTH:
            bottom += wall("───")
        else:
            bottom += "   "

        bottom += wall("┼")

    print(bottom)


if __name__ == "__main__":
    pass
