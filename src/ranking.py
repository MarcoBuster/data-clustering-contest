import config
from .categorization import load_cat_profiles, cat_contents
from .news_threads import divide_in_threads

EXTENDED_CATEGORIES = [*config.CATEGORIES, "other", "any"]
EXTENDED_CATEGORIES_INDEX = {c: EXTENDED_CATEGORIES.index(c) for c in EXTENDED_CATEGORIES}


def rank_threads(path):
    threads, index_parsed_files = divide_in_threads(path)
    cat_profiles = load_cat_profiles()

    result = []
    for category in EXTENDED_CATEGORIES:
        result.append({
            "category": category,
            "threads": [],
        })

    for thread in threads:
        thread_contents = ""
        if len(thread["articles"]) == 0:
            continue
        for file in thread["articles"]:
            thread_contents += ('\n' + index_parsed_files[file]["contents"])
        category = cat_contents(thread_contents, index_parsed_files[file]["lang"], cat_profiles)
        if category is None:
            category = "other"
        result[EXTENDED_CATEGORIES_INDEX[category]]["threads"].append(thread)
        result[EXTENDED_CATEGORIES_INDEX["any"]]["threads"].append(thread)

    for i in range(len(result)):
        result[i]["threads"].sort(
            key=lambda t: sum([*[index_parsed_files[e]["ranking_score"] for e in t["articles"]], len(t["articles"]) * 2]),
            reverse=True
        )
    return result
