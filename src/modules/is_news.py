import glob
import multiprocessing as mp

from .. import parser


def process(path):
    files = glob.glob(path + '*.html')
    pool = mp.Pool(processes=8)
    futures = {}
    for file in files:
        futures[file] = pool.apply_async(parser.parse_file, (file, ), {'compute_news_score': True})
    pool.close()
    pool.join()

    result = {"articles": []}
    for future in futures:
        parsed_file = futures[future].get()
        if parsed_file["news_score"]:
            result["articles"].append(parsed_file["filename"])
    return result
