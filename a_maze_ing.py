#!/usr/bin/env python3

from typing import Any
import random
import sys

import validate as val
import maze
import maze_solver as ms


def main() -> None:
    """Main function of the project"""
    config_file: str = val.get_config_file_name()
    config_info: str = val.load_maze_info_from_file(config_file)
    maze_info: dict[str, Any] = val.process_maze_info(config_info)
    maze_info = val.test_maze_info(maze_info)

    maze_hex = maze.create_maze(maze_info['WIDTH'], maze_info['HEIGHT'])
    maze_visited: list[list[bool]] = maze.initialize_visited(
        maze_info['WIDTH'], 
        maze_info['HEIGHT']
        )
    maze_visited[maze_info['ENTRY'][1]][maze_info['ENTRY'][0]] = True

    stack: list[tuple[int, int]] = [
        (maze_info['ENTRY'][0], 
         maze_info['ENTRY'][1])
         ]

    random.seed(maze_info["SEED"])
    while stack:
        x, y = stack[-1]
        neighbors = maze.get_unvisited_neighbors(
            x, y, maze_info['WIDTH'], maze_info['HEIGHT'], maze_visited
        )

        if neighbors:
            neighbor_x, neighbor_y, direction = random.choice(neighbors)
            maze.open_passage(maze_hex, x, y, direction)
            maze_visited[neighbor_y][neighbor_x] = True
            stack.append((neighbor_x, neighbor_y))
        else:
            stack.pop()

    if not val.check_wall_consistency(maze_hex):
        print("Error: Maze wall consistency check failed.")
        exit(1)
    else:
        print("Maze wall consistency check passed.")

    maze.display_maze(maze_hex)

    path: list[str] = ms.find_shortest_path(
        maze_hex, 
        maze_info['ENTRY'], 
        maze_info['EXIT']
        )


    val.save_maze_info_to_file(maze_info, maze_hex, path)


if __name__ == "__main__":
    main()
