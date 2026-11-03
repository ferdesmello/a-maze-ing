#!/usr/bin/env python3

import sys
from typing import Any


def get_config_file_name() -> str:
    """Get the config file name from command line arguments or use default.

    Returns:
        str: The config file name
    """
    if len(sys.argv) > 2:
        print("Error: too many arguments.")
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)
    if len(sys.argv) == 2:
        return sys.argv[1]
    print("No config file provided.")
    print("Using default config file: config.txt")
    return "config.txt"


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
    except FileNotFoundError:
        print(f"Error: '{filename}' file not found.")
        sys.exit(1)
    except (OSError, UnicodeDecodeError):
        print(f"Error: could not read '{filename}' as a text file.")
        sys.exit(1)
    print("Maze info loaded successfully:")
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
            exit_file.write(f"{maze_info['ENTRY'][0]},"
                            f"{maze_info['ENTRY'][1]}\n")
            exit_file.write(f"{maze_info['EXIT'][0]},"
                            f"{maze_info['EXIT'][1]}\n")

            exit_file.write("".join(path) + "\n")

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
    processed_info: dict[str, Any] = {}

    for number, line in enumerate(config_info.splitlines(), start=1):
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        if line.count("=") != 1:
            print(f"Error: line {number} is not a KEY=VALUE pair: '{line}'")
            sys.exit(1)
        key, value = line.split("=")
        key = key.strip()
        if key in processed_info:
            print(f"Error: line {number}: key '{key}' is defined twice.")
            sys.exit(1)
        processed_info[key] = value.strip()

    print("Maze info processed successfully.")
    return processed_info


def parse_point(name: str, text: str) -> tuple[int, int]:
    """Convert 'x,y' into a tuple of two integers.

    Args:
        name (str): The key name, used in error messages
        text (str): The value to convert, e.g. "0,0"
    Returns:
        tuple[int, int]: The (x, y) coordinates
    """
    parts: list[str] = text.split(",")
    if len(parts) != 2:
        print(f"Error: {name} must have exactly two values: x,y")
        sys.exit(1)
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        print(f"Error: {name} coordinates must be integers.")
        sys.exit(1)


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
        maze_info['ENTRY'] = parse_point('ENTRY', maze_info['ENTRY'])
        maze_info['EXIT'] = parse_point('EXIT', maze_info['EXIT'])
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
