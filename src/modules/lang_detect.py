import multiprocessing as mp

import langdetect

import config
from .. import common, parser


def detect(text):
    try:
        return langdetect.detect(text)
    except:
        return None


def process(path):
    pool = mp.Pool(processes=config.CONCURRENT_PROCESSES)
    futures = {}
    files = common.get_files(path)
    for file in files:
        futures[file] = pool.apply_async(parser.parse_file, (file, ))
    pool.close()
    pool.join()

    results = [{"lang_code": l, "articles": []} for l in config.LANGUAGES]
    for future in futures:
        parsed_file = futures[future].get()
        if parsed_file["lang"] not in config.LANGUAGES:
            continue
        results[config.LANGUAGES.index(parsed_file["lang"])]["articles"].append(parsed_file["filename"])
    return results
