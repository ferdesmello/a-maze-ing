#!/usr/bin/env python3

import sys
from typing import Any

import validate as val
import display
from mazegen import MazeGenerator


def main() -> None:
    """Main function of the project"""
    config_file: str = val.get_config_file_name()
    config_info: str = val.load_maze_info_from_file(config_file)
    maze_info: dict[str, Any] = val.process_maze_info(config_info)
    maze_info = val.test_maze_info(maze_info)

    try:
        generator: MazeGenerator = MazeGenerator(
            maze_info['WIDTH'],
            maze_info['HEIGHT'],
            maze_info['ENTRY'],
            maze_info['EXIT'],
            perfect=maze_info['PERFECT'],
            seed=maze_info.get('SEED')
        )
        generator.generate()

        if not generator.is_consistent():
            print("Error: Maze wall consistency check failed.")
            sys.exit(1)
        print("Maze wall consistency check passed.")

        maze_hex: list[list[int]] = generator.grid
        path: list[str] = generator.solve()

        display.display_maze(
            maze_hex=maze_hex, 
            path=path, 
            start=maze_info['ENTRY'])

    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

    val.save_maze_info_to_file(maze_info, maze_hex, path)


if __name__ == "__main__":
    main()
