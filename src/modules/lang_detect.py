import langdetect

from .. import common, parser
import config

import multiprocessing as mp


def detect(text):
    try:
        return langdetect.detect(text)
    except:
        return None


def process(path):
    pool = mp.Pool(processes=8)
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
