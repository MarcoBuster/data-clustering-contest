from .news_threads import split_in_threads
from . import parser
from .categorization import load_cat_profiles, cat_contents, parse_file
import config


EXTENDED_CATEGORIES = [*config.CATEGORIES, "other", "any"]
EXTENDED_CATEGORIES_INDEX = {c: EXTENDED_CATEGORIES.index(c) for c in EXTENDED_CATEGORIES}


def rank_threads(path):
    threads = split_in_threads(path)
    cat_profiles = load_cat_profiles()

    result = []
    for category in EXTENDED_CATEGORIES:
        result.append({
            "category": category,
            "threads": [],
        })

    files_contents = {}

    for thread in threads:
        thread_contents = ""
        for file in thread["articles"]:
            with open(path + file, "r") as f:
                contents = f.read()
                thread_contents += ('\n' + parse_file(contents))
                files_contents = {**files_contents, file: contents}
        category = cat_contents(thread_contents, cat_profiles)
        if category is None:
            category = "other"
        result[EXTENDED_CATEGORIES_INDEX[category]]["threads"].append(thread)
        result[EXTENDED_CATEGORIES_INDEX["any"]]["threads"].append(thread)

    for i in range(len(result)):
        result[i]["threads"].sort(
            key=lambda t: sum([*[parser.ranking_score(files_contents[e]) for e in t["articles"]], len(t["articles"]) * 2]),
            reverse=True
        )
    return result
