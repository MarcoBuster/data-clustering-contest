from src import main as src_main

import sys

SUPPORTED_ACTIONS = ["languages", "categories"]


def main():
    if len(sys.argv) < 3:
        return print('Invalid number of arguments.')

    action = sys.argv[1]
    if action not in SUPPORTED_ACTIONS:
        return print('Invalid action.')

    if action == "languages":
        src_main.language(sys.argv[2])

    if action == "categories":
        src_main.categories(sys.argv[2])


if __name__ == "__main__":
    main()
