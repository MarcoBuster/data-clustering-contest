import glob

import nltk

import config
from .. import parser
import multiprocessing as mp


def divide_in_threads(path, before_ranking=False):
    ngrams = []
    parsed_files = []
    index_parsed_files = {}
    pool = mp.Pool(processes=config.CONCURRENT_PROCESSES)
    futures = {}
    files = glob.glob(path + "*.html")
    for file in files:
        futures[file] = pool.apply_async(parser.generate_parsed_file, (file, ), {
            'pre_compute': ('news_score', 'ranking_score', 'short_ngrams', 'lang', 'category' if before_ranking else ''),
        })
    pool.close()
    pool.join()

    for future in futures:
        parsed_file = futures[future].get()
        if parsed_file.lang() not in config.LANGUAGES:
            continue
        if not parsed_file.news_score():
            continue

        ngrams.append(parsed_file.short_ngrams())
        parsed_files.append(parsed_file)
        index_parsed_files[parsed_file.filename] = parsed_file

    length = len(ngrams)
    similar = []
    for i in range(length):
        for j in range(length):
            if j < i:
                continue
            if not ngrams[i] or not ngrams[j]:
                continue
            dist = nltk.jaccard_distance(ngrams[i], ngrams[j])
            if dist < config.THREADING_MAX_DISTANCE and dist != 0:
                similar.append((parsed_files[i], parsed_files[j]))

    results = []
    for element in similar:
        not_in = True
        for r in enumerate(results):
            cond_a = element[0].filename in r[1]["articles"]
            cond_b = element[1].filename in r[1]["articles"]
            if not cond_a and not cond_b:
                continue
            elif cond_a and not cond_b:
                results[r[0]]["articles"].append(element[1].filename)
            elif not cond_a and cond_a:
                results[r[0]]["articles"].append(element[0].filename)
            not_in = False
        if not_in:
            results.append({
                "articles": [element[0].filename, element[1].filename]
            })

    for i in range(len(results)):
        results[i]["title"] = index_parsed_files[min(results[i]["articles"], key=lambda e: len(index_parsed_files[e].title))].title
        results[i]["articles"].sort(key=lambda e: index_parsed_files[e].ranking_score(), reverse=True)

    return results, index_parsed_files


def process(path):
    return divide_in_threads(path)[0]
