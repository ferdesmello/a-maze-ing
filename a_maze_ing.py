#!/usr/bin/env python3

from typing import Any

import validate as val
import maze


def main() -> None:
    """Main function of the project"""
    config_info: str = val.load_maze_info_from_file("config.txt")
    maze_info: dict[str, Any] = val.process_maze_info(config_info)
    maze_info = val.test_maze_info(maze_info)

    maze_hex = maze.create_maze(maze_info['WIDTH'], maze_info['HEIGHT'])
    maze.open_passage(maze_hex, 0, 0, "E")
    for row in maze_hex:
        for cell in row:
            print(f"{cell:X}", end=" ")
        print()

    val.save_maze_info_to_file(maze_info, maze_hex)


if __name__ == "__main__":
    main()
