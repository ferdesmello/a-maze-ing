#!/usr/bin/env python3

"""Reusable maze generation module.

Basic usage:
    from mazegen import MazeGenerator

    generator = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42,
                              perfect=False)
    generator.generate()
    grid = generator.grid        # list[list[int]], one int per cell
    path = generator.solve()     # e.g. ["E", "E", "S", ...]

Each cell is an int whose bits tell which walls are closed
(1 = closed, 0 = open): bit 0 = North, 1 = East, 2 = South, 3 = West.
"""

from collections import deque
import random
from typing import Optional


NORTH: int = 0b0001
EAST:  int = 0b0010
SOUTH: int = 0b0100
WEST:  int = 0b1000


class MazeGenerator:
    """Generate a maze with a randomized depth-first search and solve it.

    Attributes:
        width (int): Number of cells per row.
        height (int): Number of rows.
        entry (tuple[int, int]): Entry cell as (x, y).
        exit (tuple[int, int]): Exit cell as (x, y).
        perfect (bool): True for a single path between any two cells,
            False for a maze with loops and (almost) no dead-ends.
        seed (Optional[int]): Seed used for reproducible mazes.
    """
    LOGO = [
        "#...###",
        "#.....#",
        "###.###",
        "..#.#..",
        "..#.###",
    ]
    LOGO_SCALE = 1

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool = False,
        seed: Optional[int] = None
    ) -> None:
        """Create a generator (call generate() to build the maze).

        Args:
            width (int): The width of the maze
            height (int): The height of the maze
            entry (tuple[int, int]): Entry coordinates (x, y)
            exit (tuple[int, int]): Exit coordinates (x, y)
            perfect (bool): True for a perfect maze (no loops),
                False (default) for a maze with loops and almost no dead-ends
            seed (Optional[int]): Seed for reproducibility, or None
        Raises:
            ValueError: If the dimensions are not positive, if entry or
            exit are outside the maze, or if entry and exit are equal.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Maze dimensions must be positive.")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry is outside the maze.")
        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ValueError("Exit is outside the maze.")
        if entry == exit:
            raise ValueError("Entry and exit must be different points.")

        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed

        self.blocked_cells: set[tuple[int, int]] = set()

        logo_width = len(self.LOGO[0]) * self.LOGO_SCALE
        logo_height = len(self.LOGO) * self.LOGO_SCALE

        if width >= logo_width + 2 and height >= logo_height + 2:
            offset_x = (width - logo_width) // 2
            offset_y = (height - logo_height) // 2

            for y, row in enumerate(self.LOGO):
                for x, pixel in enumerate(row):
                    if pixel == "#":
                        for dy in range(self.LOGO_SCALE):
                            for dx in range(self.LOGO_SCALE):
                                self.blocked_cells.add((
                                    offset_x + x * self.LOGO_SCALE + dx,
                                    offset_y + y * self.LOGO_SCALE + dy,
                                ))

        if entry in self.blocked_cells or exit in self.blocked_cells:
            raise ValueError("Entry and exit cannot overlap the 42 logo.")

        self._rng: random.Random = random.Random(seed)
        self._grid: list[list[int]] = self._create_grid()
        self._visited: list[list[bool]] = self._initialize_visited()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def grid(self) -> list[list[int]]:
        """A copy of the maze grid (one int per cell, row by row)."""
        return [row[:] for row in self._grid]

    def generate(self) -> None:
        """Generate a new maze (randomized depth-first search).

        The depth-first search always gives a perfect maze. If perfect
        is False, dead-ends are then opened to create loops.

        Can be called several times: with the same seed, the sequence of
        mazes is always the same, but each call gives a new maze.

        Raises:
            ValueError: If perfect is False and the maze is too small
            to have two independent loops.
        """
        self._grid = self._create_grid()
        self._visited = self._initialize_visited()

        entry_x, entry_y = self.entry
        self._visited[entry_y][entry_x] = True
        stack: list[tuple[int, int]] = [self.entry]

        while stack:
            x, y = stack[-1]
            neighbors = self._get_unvisited_neighbors(x, y)

            if neighbors:
                neighbor_x, neighbor_y, direction = self._rng.choice(
                    neighbors
                )
                self.open_passage(x, y, direction)
                self._visited[neighbor_y][neighbor_x] = True
                stack.append((neighbor_x, neighbor_y))
            else:
                stack.pop()

        if not self.perfect:
            self._remove_dead_ends()
            self._ensure_loops(2)

    def solve(self) -> list[str]:
        """Find a shortest path from entry to exit using BFS.

        Returns:
            list[str]: List of directions ("N", "E", "S", "W")
            from entry to exit
        Raises:
            ValueError: If no path exists between entry and exit.
        """
        queue: deque[tuple[int, int]] = deque([self.entry])
        visited: set[tuple[int, int]] = {self.entry}
        predecessor: dict[
            tuple[int, int], tuple[tuple[int, int], str]
        ] = {}

        # Explore the maze using BFS
        while queue:
            current = queue.popleft()

            # Stop searching once we reach the exit
            if current == self.exit:
                break

            x, y = current
            for neighbor_x, neighbor_y, direction in self.get_neighbors(
                x, y
            ):
                neighbor = (neighbor_x, neighbor_y)

                # Skip visited cells and closed walls
                if neighbor in visited:
                    continue
                if not self.can_move(x, y, direction):
                    continue

                # Record how we reached this cell
                visited.add(neighbor)
                predecessor[neighbor] = (current, direction)
                queue.append(neighbor)

        if self.exit not in visited:
            raise ValueError("No path exists between entry and exit.")

        # Reconstruct the path by working backward from the exit
        path: list[str] = []
        cell = self.exit
        while cell != self.entry:
            previous, step = predecessor[cell]
            path.append(step)
            cell = previous

        path.reverse()
        return path

    def is_consistent(self) -> bool:
        """Check whether adjacent cells agree on shared walls.

        Returns:
            bool: True if the maze is consistent, False otherwise
        """
        for y in range(self.height):
            for x in range(self.width):
                current = self._grid[y][x]

                # Check the east wall.
                if x < self.width - 1:
                    neighbor = self._grid[y][x + 1]
                    if bool(current & EAST) != bool(neighbor & WEST):
                        return False

                # Check the south wall.
                if y < self.height - 1:
                    neighbor = self._grid[y + 1][x]
                    if bool(current & SOUTH) != bool(neighbor & NORTH):
                        return False

        return True

    def count_dead_ends(self) -> int:
        """Count the cells that have exactly three closed walls.

        Returns:
            int: The number of dead-ends
        """
        return len(self._get_dead_ends())

    def count_loops(self) -> int:
        """Count the independent loops of the maze.

        Assumes every cell is reachable (true for generated mazes).
        A perfect maze has 0 loops.

        Returns:
            int: The number of independent loops
        """
        open_passages = 0
        for y in range(self.height):
            for x in range(self.width):
                if x < self.width - 1 and self.can_move(x, y, "E"):
                    open_passages += 1
                if y < self.height - 1 and self.can_move(x, y, "S"):
                    open_passages += 1

        open_cells = self.width * self.height - len(self.blocked_cells)
        return open_passages - (open_cells - 1)

    def open_passage(self, x: int, y: int, direction: str) -> None:
        """Open a passage between a cell and its neighbor.

        Args:
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

        if not (0 <= neighbor_x < self.width
                and 0 <= neighbor_y < self.height):
            raise ValueError("Neighbor is outside the maze.")

        self._grid[y][x] &= ~wall
        self._grid[neighbor_y][neighbor_x] &= ~opposite

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int, str]]:
        """Return valid neighboring cells and their directions.

        Args:
            x (int): The x coordinate of the cell
            y (int): The y coordinate of the cell
        Returns:
            list[tuple[int, int, str]]: A list of tuples containing the
            coordinates and direction of valid neighboring cells
        Raises:
            ValueError: If the cell coordinates are outside the maze.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Cell coordinates are outside the maze.")

        neighbors: list[tuple[int, int, str]] = []

        if y > 0:
            neighbors.append((x, y - 1, "N"))
        if x < self.width - 1:
            neighbors.append((x + 1, y, "E"))
        if y < self.height - 1:
            neighbors.append((x, y + 1, "S"))
        if x > 0:
            neighbors.append((x - 1, y, "W"))

        return neighbors

    def can_move(self, x: int, y: int, direction: str) -> bool:
        """Return whether a passage is open in the given direction.

        Args:
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

        return (self._grid[y][x] & wall) == 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_grid(self) -> list[list[int]]:
        """Create a grid with all four walls closed in every cell.

        Returns:
            list[list[int]]: The created maze grid
        """
        cells: list[list[int]] = []

        for _ in range(self.height):
            row: list[int] = []
            for _ in range(self.width):
                row.append(0b1111)
            cells.append(row)

        return cells

    def _initialize_visited(self) -> list[list[bool]]:
        """Create a 2D list (True/False) to track visited cells.

        Args:
            self (MazeGenerator): The MazeGenerator instance
        Returns:
            list[list[bool]]: A 2D list initialized to (mostly) False
        """
        visited = [
            [False] * self.width
            for _ in range(self.height)
        ]

        for x, y in self.blocked_cells:
            visited[y][x] = True

        return visited

    def _get_unvisited_neighbors(
        self, x: int, y: int
    ) -> list[tuple[int, int, str]]:
        """Return neighboring cells that have not been visited.

        Args:
            x (int): The x coordinate of the cell
            y (int): The y coordinate of the cell
        Returns:
            list[tuple[int, int, str]]: A list of tuples containing the
            coordinates and direction of unvisited neighboring cells
        """
        not_visited_neighbors: list[tuple[int, int, str]] = []
        for neighbor_x, neighbor_y, direction in self.get_neighbors(x, y):
            if not self._visited[neighbor_y][neighbor_x]:
                not_visited_neighbors.append(
                    (neighbor_x, neighbor_y, direction)
                )
        return not_visited_neighbors

    def _is_dead_end(self, x: int, y: int) -> bool:
        """Return whether a cell has exactly three closed walls."""
        walls = 0
        for wall in (NORTH, EAST, SOUTH, WEST):
            if self._grid[y][x] & wall:
                walls += 1
        return walls == 3

    def _get_dead_ends(self) -> list[tuple[int, int]]:
        """Return the coordinates of all dead-end cells."""
        dead_ends: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if self._is_dead_end(x, y):
                    dead_ends.append((x, y))
        return dead_ends

    def _is_open_block(self, left: int, top: int) -> bool:
        """Return whether a 3x3 block has no walls between its cells.

        Args:
            left (int): The x coordinate of the block's top-left cell
            top (int): The y coordinate of the block's top-left cell
        Returns:
            bool: True if the whole 3x3 block is open
        """
        if (left < 0 or top < 0
                or left + 2 >= self.width or top + 2 >= self.height):
            return False

        for y in range(top, top + 3):
            for x in range(left, left + 3):
                if x < left + 2 and not self.can_move(x, y, "E"):
                    return False
                if y < top + 2 and not self.can_move(x, y, "S"):
                    return False

        return True

    def _has_open_area_near(
        self,
        x: int,
        y: int,
        neighbor_x: int,
        neighbor_y: int
    ) -> bool:
        """Return whether a 3x3 open block exists around two cells.
            Only the blocks that contain one of the two cells are checked.
        Args:
            x (int): The x coordinate of the first cell
            y (int): The y coordinate of the first cell
            neighbor_x (int): The x coordinate of the second cell
            neighbor_y (int): The y coordinate of the second cell
        Returns:
            bool: True if a 3x3 open block exists, False otherwise
        """
        left = min(x, neighbor_x) - 2
        right = max(x, neighbor_x)
        top = min(y, neighbor_y) - 2
        bottom = max(y, neighbor_y)

        for block_y in range(top, bottom + 1):
            for block_x in range(left, right + 1):
                if self._is_open_block(block_x, block_y):
                    return True

        return False

    def _try_open_passage(
        self, x: int, y: int, neighbor_x: int, neighbor_y: int,
        direction: str
    ) -> bool:
        """Open a passage unless it creates a 3x3 open area.

        Args:
            x (int): The x coordinate of the cell
            y (int): The y coordinate of the cell
            neighbor_x (int): The x coordinate of the neighbor
            neighbor_y (int): The y coordinate of the neighbor
            direction (str): The direction from the cell to the neighbor
        Returns:
            bool: True if the passage was opened, False if it was
            undone because it would create a 3x3 open area
        """
        old_cell = self._grid[y][x]
        old_neighbor = self._grid[neighbor_y][neighbor_x]

        self.open_passage(x, y, direction)

        if self._has_open_area_near(x, y, neighbor_x, neighbor_y):
            self._grid[y][x] = old_cell
            self._grid[neighbor_y][neighbor_x] = old_neighbor
            return False

        return True

    def _remove_dead_ends(self) -> None:
        """Open one wall in each dead-end to join it to another corridor.

        A dead-end that cannot be opened without creating a 3x3 open
        area is left as it is.
        """
        dead_ends = self._get_dead_ends()
        self._rng.shuffle(dead_ends)

        for x, y in dead_ends:
            # A previous removal may have already fixed this cell.
            if not self._is_dead_end(x, y):
                continue

            # Do not modify blocked logo cells.
            if (x, y) in self.blocked_cells:
                continue

            closed_walls: list[tuple[int, int, str]] = []
            for neighbor_x, neighbor_y, direction in self.get_neighbors(
                x, y
            ):
                # Do not open passages into blocked logo cells.
                if (neighbor_x, neighbor_y) in self.blocked_cells:
                    continue

                if not self.can_move(x, y, direction):
                    closed_walls.append((neighbor_x, neighbor_y, direction))

            self._rng.shuffle(closed_walls)

            # Try dead-end neighbors first: one wall fixes both cells.
            candidates = [wall for wall in closed_walls
                          if self._is_dead_end(wall[0], wall[1])]
            candidates += [wall for wall in closed_walls
                           if not self._is_dead_end(wall[0], wall[1])]

            for neighbor_x, neighbor_y, direction in candidates:
                if self._try_open_passage(
                    x, y, neighbor_x, neighbor_y, direction
                ):
                    break

    def _ensure_loops(self, minimum: int) -> None:
        """Open random walls until the maze has enough loops.

        Args:
            minimum (int): The minimum number of independent loops
        Raises:
            ValueError: If the maze cannot have that many loops.
        """
        closed_walls: list[tuple[int, int, str]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (
                    x < self.width - 1
                    and (x, y) not in self.blocked_cells
                    and (x + 1, y) not in self.blocked_cells
                    and not self.can_move(x, y, "E")
                ):
                    closed_walls.append((x, y, "E"))

                if (
                    y < self.height - 1
                    and (x, y) not in self.blocked_cells
                    and (x, y + 1) not in self.blocked_cells
                    and not self.can_move(x, y, "S")
                ):
                    closed_walls.append((x, y, "S"))
        self._rng.shuffle(closed_walls)

        loops = self.count_loops()
        for x, y, direction in closed_walls:
            if loops >= minimum:
                break
            if direction == "E":
                neighbor_x, neighbor_y = x + 1, y
            else:
                neighbor_x, neighbor_y = x, y + 1
            if self._try_open_passage(x, y, neighbor_x, neighbor_y,
                                      direction):
                loops += 1

        if loops < minimum:
            raise ValueError(
                "Maze too small for a non-perfect maze (it needs at "
                "least two independent loops). Use PERFECT=True or a "
                "bigger maze."
            )


if __name__ == "__main__":
    pass
