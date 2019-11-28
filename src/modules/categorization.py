import glob
import multiprocessing as mp

import config
from .. import parser


def process(path):
    result = []
    for category in config.CATEGORIES:
        result.append({
            "category": category,
            "articles": []
        })
    result.append({
        "category": "other",
        "articles": []
    })

    files = glob.glob(path + "*.html")
    futures = {}
    pool = mp.Pool(processes=config.CONCURRENT_PROCESSES)
    for file in files:
        futures[file.split('/')[-1]] = pool.apply_async(parser.generate_parsed_file, (file, ), {
            'pre_compute': ('category', 'news_score', )
        })
    pool.close()
    pool.join()

    for file in futures:
        parsed_file = futures[file].get()
        if parsed_file.lang() not in config.LANGUAGES:
            continue
        if not parsed_file.news_score():
            continue

        result[result.index(next(i for i in result if i["category"] == parsed_file.category()))]["articles"].append(file)
    return result
