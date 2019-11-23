import glob

import nltk

import config
from . import parser
from .training import train


def divide_in_threads(path):
    ngrams = []
    parsed_files = []
    index_parsed_files = {}
    for file in glob.glob(path + "*.html"):
        parsed_file = parser.parse_file(file, compute_news_score=True, compute_ranking_score=True)
        if parsed_file["lang"] not in config.LANGUAGES:
            continue
        if not parsed_file["news_score"]:
            continue

        ngram_string = (parsed_file["title"] if parsed_file["title"] else '') + ' '.join(parsed_file["contents"].split()[:20])
        ngrams.append(train.generate_ngrams(ngram_string, 3))
        parsed_files.append(parsed_file)
        index_parsed_files[parsed_file["filename"]] = parsed_file

    length = len(ngrams)
    similar = []
    for i in range(length):
        for j in range(length):
            if j < i:
                continue
            dist = nltk.jaccard_distance(ngrams[i], ngrams[j])
            if dist < config.THREADING_MAX_DISTANCE and dist != 0:
                similar.append((parsed_files[i], parsed_files[j]))

    threads = []
    for element in similar:
        not_in = True
        for r in enumerate(threads):
            cond_a = element[0]["filename"] in r[1]["articles"]
            cond_b = element[1]["filename"] in r[1]["articles"]
            if not cond_a and not cond_b:
                continue
            elif cond_a and not cond_b:
                threads[r[0]]["articles"].append(element[1]["filename"])
            elif not cond_a and cond_a:
                threads[r[0]]["articles"].append(element[0]["filename"])
            not_in = False
        if not_in:
            threads.append({
                "articles": [element[0]["filename"], element[1]["filename"]]
            })

    for i in range(len(threads)):
        threads[i]["title"] = index_parsed_files[min(threads[i]["articles"], key=lambda e: len(index_parsed_files[e]["title"]))]["title"]
        threads[i]["articles"].sort(key=lambda e: index_parsed_files[e]["ranking_score"], reverse=True)
    return threads, index_parsed_files


def generate_threads(path):
    return divide_in_threads(path)[0]
