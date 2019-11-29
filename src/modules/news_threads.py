import glob

import nltk

import config
from .. import parser
import multiprocessing as mp


def _get_similar_articles(parsed_files):
    length = len(parsed_files)
    similar = []
    for i in range(length):
        for j in range(length):
            if j <= i:
                continue
            if not parsed_files[i] or not parsed_files[j]:
                continue
            dist = nltk.jaccard_distance(parsed_files[i].short_ngrams(),
                                         parsed_files[j].short_ngrams())
            if dist < config.THREADING_MAX_DISTANCE and dist != 0:
                similar.append((parsed_files[i], parsed_files[j]))
    return similar


def divide_in_threads(path):
    pool = mp.Pool(processes=config.CONCURRENT_PROCESSES)
    futures = {}
    files = glob.glob(path + "*.html")
    for file in files:
        futures[file] = pool.apply_async(parser.generate_parsed_file, (file, ), {
            'pre_compute': ('news_score', 'ranking_score', 'short_ngrams', 'lang', 'category'),
        })
    pool.close()
    pool.join()

    parsed_files = dict((l, dict((l, list()) for l in [*config.CATEGORIES, "other"])) for l in config.LANGUAGES)
    index_parsed_files = {}
    for future in futures:
        parsed_file = futures[future].get()
        if parsed_file.lang() not in config.LANGUAGES:
            continue
        if not parsed_file.news_score():
            continue

        parsed_files[parsed_file.lang()][parsed_file.category()].append(parsed_file)
        index_parsed_files[parsed_file.filename] = parsed_file

    pool = mp.Pool(processes=config.CONCURRENT_PROCESSES)
    futures = []
    for lang in parsed_files:
        for cat in parsed_files[lang]:
            futures.append(pool.apply_async(_get_similar_articles, kwds={
                'parsed_files': parsed_files[lang][cat],
            }))

    similar = []
    for future in futures:
        similar.extend(future.get())

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
