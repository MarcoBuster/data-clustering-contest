import sys

from src import main as src_main
from src import common

SUPPORTED_ACTIONS = ["languages", "news", "categories", "threads", "top"]


def main():
    if len(sys.argv) < 3:
        return common.print_json({
            'ok': False,
            'error': 'Invalid number of arguments',
        })

    action = sys.argv[1]
    if action not in SUPPORTED_ACTIONS:
        return common.print_json({
            'ok': False,
            'error': 'Invalid action selected',
        })

    path = sys.argv[2]
    if not path.endswith('/'):
        path += '/'

    if action == "languages":
        src_main.language(path)

    elif action == "news":
        src_main.news(path)

    elif action == "categories":
        src_main.categories(path)

    elif action == "threads":
        src_main.threads(path)

    elif action == "top":
        src_main.top(path)


if __name__ == "__main__":
    main()
