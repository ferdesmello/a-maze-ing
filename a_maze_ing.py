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

    show_path = False
    wall_colors = [
        "\033[1;37m",  # White (initial color)
        "\033[1;31m",  # Red
        "\033[1;32m",  # Green
        "\033[1;35m",  # Purple
    ]
    wall_color_index = 0

    try:
        generator: MazeGenerator = MazeGenerator(
            maze_info['WIDTH'],
            maze_info['HEIGHT'],
            maze_info['ENTRY'],
            maze_info['EXIT'],
            perfect=maze_info['PERFECT'],
            seed=maze_info.get('SEED')
        )

        if not generator.blocked_cells:
            print("Error: the maze is too small to draw the 42 pattern.")

        generator.generate()

        if not generator.is_consistent():
            print("Error: Maze wall consistency check failed.")
            sys.exit(1)
        print("Maze wall consistency check passed.")

        maze_hex: list[list[int]] = generator.grid
        path: list[str] = generator.solve()

        display.display_maze(
            maze_hex=maze_hex,
            path=path if show_path else None,
            wall_color=wall_colors[wall_color_index],
            start_cell=maze_info['ENTRY'],
            exit_cell=maze_info['EXIT'],
            blocked_cells=generator.blocked_cells)
        val.save_maze_info_to_file(maze_info, maze_hex, path)

        while True:
            print("=== A-Maze-ing ===")
            print("1. Re-generate a new maze")
            print("2. Show / Hide the shortest path")
            print("3. Rotate the wall colours")
            print("4. Quit")

            try:
                choice = input("Choice? (1-4): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting the program. Goodbye!")
                sys.exit(0)

            if choice == '1':
                print("[Action] Generating a new maze...\n")
                generator.generate()

                if not generator.is_consistent():
                    print("Error: Maze wall consistency check failed.")
                    sys.exit(1)

                maze_hex = generator.grid
                path = generator.solve()

                display.display_maze(
                    maze_hex=maze_hex,
                    path=path if show_path else None,
                    wall_color=wall_colors[wall_color_index],
                    start_cell=maze_info['ENTRY'],
                    exit_cell=maze_info['EXIT'],
                    blocked_cells=generator.blocked_cells)
                val.save_maze_info_to_file(maze_info, maze_hex, path)

            elif choice == '2':
                print("Changing the visibility of the shortest path...\n")
                show_path = not show_path
                display.display_maze(
                    maze_hex=maze_hex,
                    path=path if show_path else None,
                    wall_color=wall_colors[wall_color_index],
                    start_cell=maze_info['ENTRY'],
                    exit_cell=maze_info['EXIT'],
                    blocked_cells=generator.blocked_cells)

            elif choice == '3':
                print("Rotating the wall colours...\n")
                wall_color_index = (wall_color_index + 1) % len(wall_colors)
                display.display_maze(
                    maze_hex=maze_hex,
                    path=path if show_path else None,
                    wall_color=wall_colors[wall_color_index],
                    start_cell=maze_info['ENTRY'],
                    exit_cell=maze_info['EXIT'],
                    blocked_cells=generator.blocked_cells)

            elif choice == '4':
                print("Exiting the program. Goodbye!")
                sys.exit()

            else:
                print("\nInvalid option! "
                      "Please choose a number from 1 to 4.\n")

    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
