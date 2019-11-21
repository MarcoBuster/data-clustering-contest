from . import parser, lang_detect
from .training import train

import glob
import nltk
import config


def split_in_threads(path):
    ngrams = []
    files = []
    files_contents = {}
    for file in glob.glob(path + '*.html'):
        with open(file, 'r') as f:
            contents = f.read()
            title, summary = parser.get_title_and_summary(contents)
            if lang_detect.detect(title if title else '' + ' ' + summary) not in config.LANGUAGES:
                continue
        file_name = file.split('/')[-1]
        files.append(file_name)
        files_contents[file_name] = (title, contents)
        ngrams.append(train.generate_ngrams(title if title else '' + ' ' + summary, 3))

    length = len(ngrams)
    similar = []
    for i in range(length):
        for j in range(length):
            if j < i:
                continue
            dist = nltk.jaccard_distance(ngrams[i], ngrams[j])
            if dist < config.THREADING_MAX_DISTANCE and dist != 0:
                similar.append((files[i], files[j]))

    threads = []
    for element in similar:
        not_in = True
        for r in enumerate(threads):
            cond_a = element[0] in r[1]["articles"]
            cond_b = element[1] in r[1]["articles"]
            if not cond_a and not cond_b:
                continue
            elif cond_a and not cond_b:
                threads[r[0]]["articles"].append(element[1])
            elif not cond_a and cond_a:
                threads[r[0]]["articles"].append(element[0])
            not_in = False
        if not_in:
            threads.append({
                "articles": [element[0], element[1]]
            })

    for i in range(len(threads)):
        threads[i]["title"] = files_contents[min(threads[i]["articles"], key=lambda e: len(files_contents[e][0]))][0]
        threads[i]["articles"].sort(key=lambda e: parser.ranking_score(files_contents[e][1]), reverse=True)
    return threads
