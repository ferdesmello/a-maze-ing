#!/usr/bin/env python3

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

    """
    # Hexadecimal values for the walls
    0b0000: 0: all walls open
    0b0001: 1: NORTH
    0b0010: 2: EAST
    0b0011: 3
    0b0100: 4: SOUTH
    0b0101: 5
    0b0110: 6
    0b0111: 7
    0b1000: 8: WEST
    0b1001: 9
    0b1010: 10, a
    0b1011: 11, b
    0b1100: 12, c
    0b1101: 13, d
    0b1110: 14, e
    0b1111: 15, f: all walls closed
    """

    NORTH: int = 0b0001
    EAST:  int = 0b0010
    SOUTH: int = 0b0100
    WEST:  int = 0b1000

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


if __name__ == "__main__":
    pass
