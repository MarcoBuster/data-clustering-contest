import config
from .news_threads import divide_in_threads

EXTENDED_CATEGORIES = [*config.CATEGORIES, "other", "any"]
EXTENDED_CATEGORIES_INDEX = {c: EXTENDED_CATEGORIES.index(c) for c in EXTENDED_CATEGORIES}


def process(path):
    threads, parsed_files = divide_in_threads(path)

    results = []
    for category in EXTENDED_CATEGORIES:
        results.append({
            "category": category,
            "threads": [],
        })

    for thread in threads:
        thread_categories = []
        if len(thread["articles"]) == 0:
            continue
        for file in thread["articles"]:
            thread_categories.append(parsed_files[file].category())
        category = max(set(thread_categories), key=thread_categories.count)
        results[EXTENDED_CATEGORIES_INDEX[category]]["threads"].append(thread)
        results[EXTENDED_CATEGORIES_INDEX["any"]]["threads"].append(thread)

    for i in range(len(results)):
        results[i]["threads"].sort(
            key=lambda t: sum([*[parsed_files[e].ranking_score for e in t["articles"]], len(t["articles"]) * 2]),
            reverse=True
        )
    return results
