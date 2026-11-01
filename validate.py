#!/usr/bin/env python3

import sys
from typing import Any


def get_config_file_name() -> str:
    """Get the config file name from command line arguments or use default.

    Returns:
        str: The config file name
    """
    if len(sys.argv) == 2:
        config_file: str = sys.argv[1]
    else:
        print("No config file provided.")
        print("Using default config file: config.txt")
        config_file = "config.txt"
    return config_file


def load_maze_info_from_file(filename: str) -> str:
    """Loads maze info from a file

    Args:
        filename (str): the input file name to load the maze info from
    Returns:
        str: The content of the file.
    """
    try:
        with open(filename, "r") as config_file:
            config_info: str = config_file.read()
            print("Maze info loaded successfully:")
    except FileNotFoundError:
        print(f"Error: '{filename}' file not found.")
        sys.exit(1)
    return config_info


def save_maze_info_to_file(
        maze_info: dict[str, Any],
        maze_hex: list[list[int]],
        path: list[str]
        ) -> None:
    """Saves output maze info into a file

    Args:
        maze_info (dict[str, Any]): The maze info to save
        maze_hex (list[list[int]]): The maze grid to save
        path (list[str]): The shortest path
    """
    filename: str = maze_info["OUTPUT_FILE"]
    try:
        with open(filename, "w") as exit_file:
            for row in maze_hex:
                for cell in row:
                    exit_file.write(f"{cell:x}")
                exit_file.write("\n")

            exit_file.write("\n")
            exit_file.write(f"{maze_info['ENTRY'][0]}, "
                            f"{maze_info['ENTRY'][1]}")
            exit_file.write("     # entry  (x, y)\n")
            exit_file.write(f"{maze_info['EXIT'][0]}, "
                            f"{maze_info['EXIT'][1]}")
            exit_file.write("     # exit  (x, y)\n")

            for direction in path:
                exit_file.write(direction)

        print(f"Maze info saved in file '{filename}'.")
    except IOError:
        print(f"Error: Could not write to file '{filename}'.")
        sys.exit(1)


def process_maze_info(config_info: str) -> dict[str, Any]:
    """Processes the loaded maze info into a dictionary

    Args:
        config_info (str): The loaded maze info to process
    Returns:
        dict[str, Any]: The processed maze info
    """
    lines: list[str] = config_info.splitlines()
    processed_info: dict[str, Any] = {}
    try:
        for line in lines:
            if line.strip() == "" or line.startswith("#"):
                continue
            if '=' in line:
                key: str
                value: str
                key, value = line.split('=')
                processed_info[key.strip()] = value.strip()

    except ValueError:
        print("Error: Invalid maze info format.")
        sys.exit(1)

    print("Maze info processed successfully.")
    return processed_info


def test_maze_info(maze_info: dict[str, Any]) -> dict[str, Any]:
    """Tests the loaded maze info

    Args:
        maze_info (dict[str, Any]): The loaded maze info to test
    """

    needed_keys: list[str] = [
        'WIDTH',
        'HEIGHT',
        'ENTRY',
        'EXIT',
        'OUTPUT_FILE',
        'PERFECT'
        ]

    if not all(key in maze_info for key in needed_keys):
        print("Error: Missing keys in maze info.")
        sys.exit(1)

    allowed_keys: set[str] = set(needed_keys) | {'SEED'}
    if not set(maze_info.keys()).issubset(allowed_keys):
        print("Error: Extra keys in maze info.")
        sys.exit(1)

    for value in maze_info.values():
        if value == "":
            print("Error: Empty value in maze info.")
            sys.exit(1)

    try:
        maze_info['WIDTH'] = int(maze_info['WIDTH'])
        maze_info['HEIGHT'] = int(maze_info['HEIGHT'])
        maze_info['ENTRY'] = tuple(map(int, maze_info['ENTRY'].split(',')))
        maze_info['EXIT'] = tuple(map(int, maze_info['EXIT'].split(',')))
        maze_info['OUTPUT_FILE'] = str(maze_info['OUTPUT_FILE'])
        maze_info['PERFECT'] = str(maze_info['PERFECT'])
    except ValueError:
        print("Error: Invalid value type in maze info.")
        sys.exit(1)

    if not (0 < maze_info['WIDTH'] <= 100):
        print("Error: WIDTH must be positive integer between 1 and 100.")
        sys.exit(1)
    if not (0 < maze_info['HEIGHT'] <= 100):
        print("Error: HEIGHT must be positive integer between 1 and 100.")
        sys.exit(1)

    if not (0 <= maze_info['ENTRY'][0] < maze_info['WIDTH']):
        print("Error: ENTRY x coordinate must be within the maze dimensions.")
        sys.exit(1)
    if not (0 <= maze_info['ENTRY'][1] < maze_info['HEIGHT']):
        print("Error: ENTRY y coordinate must be within the maze dimensions.")
        sys.exit(1)

    if not (0 <= maze_info['EXIT'][0] < maze_info['WIDTH']):
        print("Error: EXIT x coordinate must be within the maze dimensions.")
        sys.exit(1)
    if not (0 <= maze_info['EXIT'][1] < maze_info['HEIGHT']):
        print("Error: EXIT y coordinate must be within the maze dimensions.")
        sys.exit(1)

    if ((maze_info['ENTRY'][0] == maze_info['EXIT'][0]) and
            (maze_info['ENTRY'][1] == maze_info['EXIT'][1])):
        print("Error: ENTRY and EXIT must be different points.")
        sys.exit(1)

    if maze_info['PERFECT'].strip() == "True":
        maze_info['PERFECT'] = True
    elif maze_info['PERFECT'].strip() == "False":
        maze_info['PERFECT'] = False
    else:
        print("Error: PERFECT must be 'True' or 'False'.")
        sys.exit(1)

    if "SEED" in maze_info.keys():
        try:
            maze_info['SEED'] = int(maze_info['SEED'])
        except ValueError:
            print("Error: SEED must be an integer.")
            sys.exit(1)

        if not (0 <= maze_info['SEED'] <= 10000):
            print("Error: SEED must be positive integer between 0 and 10000.")
            sys.exit(1)

    print("Maze info tested successfully.")
    return maze_info


if __name__ == "__main__":
    pass
