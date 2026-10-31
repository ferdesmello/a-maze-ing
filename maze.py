#!/usr/bin/env python3

NORTH: int = 0b0001
EAST:  int = 0b0010
SOUTH: int = 0b0100
WEST:  int = 0b1000


def create_maze(width: int, height: int) -> list[list[int]]:
    """Create a grid with all four walls closed in every cell.

    Args:
        width (int): The width of the maze
        height (int): The height of the maze
    Returns:
        list[list[int]]: The created maze grid
    """
    cells: list[list[int]] = []

    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            row.append(0b1111)
        cells.append(row)

    return cells


def open_passage(
    maze_hex: list[list[int]],
    x: int,
    y: int,
    direction: str
) -> None:
    """Open a passage between a cell and its neighbor.

    Args:
        maze_hex (list[list[int]]): The maze grid
        x (int): The x coordinate of the cell
        y (int): The y coordinate of the cell
        direction (str): The direction to open the passage
        ("N", "E", "S", "W")
    Raises:
        ValueError: If the direction is invalid or the neighbor
        is outside the maze.
    """

    if direction == "N":
        neighbor_x, neighbor_y = x, y - 1
        wall, opposite = NORTH, SOUTH
    elif direction == "E":
        neighbor_x, neighbor_y = x + 1, y
        wall, opposite = EAST, WEST
    elif direction == "S":
        neighbor_x, neighbor_y = x, y + 1
        wall, opposite = SOUTH, NORTH
    elif direction == "W":
        neighbor_x, neighbor_y = x - 1, y
        wall, opposite = WEST, EAST
    else:
        raise ValueError("Direction must be N, E, S, or W.")

    height = len(maze_hex)
    width = len(maze_hex[0])

    if not (0 <= neighbor_x < width and 0 <= neighbor_y < height):
        raise ValueError("Neighbor is outside the maze.")

    maze_hex[y][x] &= ~wall
    maze_hex[neighbor_y][neighbor_x] &= ~opposite


def get_neighbors(
    x: int,
    y: int,
    width: int,
    height: int
) -> list[tuple[int, int, str]]:
    """Return valid neighboring cells and their directions.
    
    Args:
        x (int): The x coordinate of the cell
        y (int): The y coordinate of the cell
        width (int): The width of the maze
        height (int): The height of the maze
    Returns:
        list[tuple[int, int, str]]: A list of tuples containing the
        coordinates and direction of valid neighboring cells
    Raises:
        ValueError: If the maze dimensions are not positive or
        the cell coordinates are outside the maze.    
    """

    if width <= 0 or height <= 0:
        raise ValueError("Maze dimensions must be positive.")
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError("Cell coordinates are outside the maze.")

    neighbors: list[tuple[int, int, str]] = []

    if y > 0:
        neighbors.append((x, y - 1, "N"))
    if x < width - 1:
        neighbors.append((x + 1, y, "E"))
    if y < height - 1:
        neighbors.append((x, y + 1, "S"))
    if x > 0:
        neighbors.append((x - 1, y, "W"))

    return neighbors


def initialize_visited(width: int, height: int) -> list[list[bool]]:
    """Initialize a 2D list to track visited cells in the maze.

    Args:
        width (int): The width of the maze
        height (int): The height of the maze
    Returns:
        list[list[bool]]: A 2D list initialized to False
    """
    maze_visited: list[list[bool]] = []
    for _ in range(height):
        maze_visited.append([False] * width)
    return maze_visited


def get_unvisited_neighbors(
    x: int,
    y: int,
    width: int,
    height: int,
    visited: list[list[bool]]
) -> list[tuple[int, int, str]]:
    """Return neighboring cells that have not been visited.

    Args:
        x (int): The x coordinate of the cell
        y (int): The y coordinate of the cell
        width (int): The width of the maze
        height (int): The height of the maze
        visited (list[list[bool]]): A 2D list indicating visited cells
    Returns:
        list[tuple[int, int, str]]: A list of tuples containing the
        coordinates and direction of unvisited neighboring cells
    """
    neighbors = get_neighbors(x, y, width, height)

    not_visited_neighbors: list[tuple[int, int, str]] = []
    for neighbor_x, neighbor_y, direction in neighbors:
        if not visited[neighbor_y][neighbor_x]:
            not_visited_neighbors.append((neighbor_x, neighbor_y, direction))
    return not_visited_neighbors


def can_move(
    maze_hex: list[list[int]],
    x: int,
    y: int,
    direction: str
) -> bool:
    """Return whether a passage is open in the given direction.
    
    Args:
        maze_hex (list[list[int]]): The maze grid
        x (int): The x coordinate of the cell
        y (int): The y coordinate of the cell
        direction (str): The direction to check ("N", "E", "S", "W")
    Returns:
        bool: True if the passage is open, False otherwise
    Raises:
        ValueError: If the direction is invalid.    
    """
    if direction == "N":
        wall = NORTH
    elif direction == "E":
        wall = EAST
    elif direction == "S":
        wall = SOUTH
    elif direction == "W":
        wall = WEST
    else:
        raise ValueError("Direction must be N, E, S, or W.")

    return (maze_hex[y][x] & wall) == 0


def display_maze(maze_hex: list[list[int]]) -> None:
    """Display the maze using ASCII characters.
    
    Args:
        maze_hex (list[list[int]]): The maze grid    
    """

    height = len(maze_hex)
    width = len(maze_hex[0])

    for y in range(height):
        # Draw the north walls of this row.
        top = ""
        for x in range(width):
            top += "+"
            if maze_hex[y][x] & NORTH:
                top += "---"
            else:
                top += "   "
        top += "+"
        print(top)

        # Draw the west and east walls.
        middle = ""
        for x in range(width):
            if maze_hex[y][x] & WEST:
                middle += "|"
            else:
                middle += " "
            middle += "   "

        if maze_hex[y][width - 1] & EAST:
            middle += "|"
        else:
            middle += " "
        print(middle)

    # Draw the south walls of the final row.
    bottom = ""
    for x in range(width):
        bottom += "+"
        if maze_hex[height - 1][x] & SOUTH:
            bottom += "---"
        else:
            bottom += "   "
    bottom += "+"
    print(bottom)


if __name__ == "__main__":
    pass
