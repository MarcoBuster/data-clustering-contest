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
                similar.append((parsed_files[i], parsed_files[j], dist))
    return similar


def _clusterize(edges):
    def _are_interlinked(cluster, vertex):
        for v in cluster:
            connected = (v, vertex) in edges or (vertex, v) in edges
            if not connected:
                return False
        return True

    def _search_in_clusters(conn):
        first, second = conn
        f_cluster = None
        s_cluster = None
        for i, cluster in enumerate(clusters):
            if first in cluster:
                f_cluster = i
            if second in cluster:
                s_cluster = i
            if f_cluster and s_cluster:
                break
        return f_cluster, s_cluster

    clusters = []
    for edge in edges:
        c_first, c_second = _search_in_clusters(edge)

        if c_first is None and c_second is None:
            clusters.append([edge[0], edge[1]])
            continue

        if c_first is not None and c_second is None:
            if _are_interlinked(clusters[c_first], edge[1]):
                clusters[c_first].append(edge[1])
            continue

        if c_first is None and c_second is not None:
            if _are_interlinked(clusters[c_second], edge[0]):
                clusters[c_second].append(edge[0])
            continue

        if c_first != c_second:
            should_merge = False
            for v in clusters[c_first]:
                should_merge = _are_interlinked(clusters[c_second], v)
                if not should_merge:
                    break
            if should_merge:
                clusters[c_first].extend(clusters[c_second])
                clusters.remove(clusters[c_second])
    return clusters


def divide_in_threads(path):
    pool = mp.Pool(processes=config.CONCURRENT_PROCESSES)
    futures = {}
    files = glob.glob(path + "*.html")
    for file in files:
        futures[file] = pool.apply_async(parser.generate_parsed_file, (file, ), {
            'pre_compute': ('news_score', 'short_ngrams', 'lang', 'category'),
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
    pool.close()
    pool.join()

    similar = []
    for future in futures:
        similar.extend(future.get())

    similar = sorted(similar, key=lambda e: e[2])
    similar = list(map(lambda e: (e[0], e[1]), similar))

    results = []
    for connected_component in _clusterize(similar):
        results.append({
            "articles": [parsed_file.filename for parsed_file in connected_component]
        })

    for i in range(len(results)):
        results[i]["title"] = index_parsed_files[min(results[i]["articles"], key=lambda e: len(index_parsed_files[e].title))].title
        results[i]["articles"].sort(key=lambda e: index_parsed_files[e].ranking_score, reverse=True)

    return results, index_parsed_files


def process(path):
    return divide_in_threads(path)[0]
