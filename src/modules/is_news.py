import glob
import multiprocessing as mp

import config
from .. import parser


def process(path):
    files = glob.glob(path + '*.html')
    pool = mp.Pool(processes=config.CONCURRENT_PROCESSES)
    futures = {}
    for file in files:
        futures[file] = pool.apply_async(parser.generate_parsed_file, (file, ), {
            'pre_compute': ('lang', 'is_news')
        })
    pool.close()
    pool.join()

    results = {"articles": []}
    for future in futures:
        parsed_file = futures[future].get()
        if parsed_file.lang() not in config.LANGUAGES:
            continue

        if parsed_file.news_score():
            results["articles"].append(parsed_file.filename)
    return results
