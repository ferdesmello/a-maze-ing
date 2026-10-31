from collections import deque
import maze


def find_shortest_path(
    maze_hex: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int]
) -> list[str]:
    """Find a shortest path from entry to exit using BFS.
    
    Arg: 
        maze_hex (list[list[int]]): The maze in hexdecimal
        entry (tuple[int, int]): Entry coordinates
        exit (tuple[int, int]): Exit coordinates
    Returns:
        list[str]: List of directions from entry to exit
    """

    queue: deque[tuple[int, int]] = deque([entry])
    visited: set[tuple[int, int]] = {entry}
    predecessor: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

    # Explore the maze using BFS
    while queue:
        current: tuple[int, int] = queue.popleft()

        # Stop searching once we reach the exit
        if current == exit:
            break

        x: int
        y: int
        x, y = current

        # Examine the neighboring cells
        for neighbor_x, neighbor_y, direction in maze.get_neighbors(
            x, y, len(maze_hex[0]), len(maze_hex)
        ):
            neighbor: tuple[int, int] = (neighbor_x, neighbor_y)

            # Skip visited cells and walls that are closed
            if neighbor in visited:
                continue

            if not maze.can_move(maze_hex, x, y, direction):
                continue

            # Record how we reached this cell
            visited.add(neighbor)
            predecessor[neighbor] = (current, direction)

            # Schedule the neighbor for exploration
            queue.append(neighbor)

    # Check whether the exit was reachable
    if exit not in visited:
        raise ValueError("No path exists between entry and exit.")

    # Reconstruct the path by working backward from the exit
    path: list[str] = []
    current = exit

    while current != entry:
        previous: str
        direction: str
        previous, direction = predecessor[current]
        path.append(direction)
        current = previous

    # Reverse the directions to get entry-to-exit order
    path.reverse()

    return path
