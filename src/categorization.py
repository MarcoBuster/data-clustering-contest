import glob
import pickle
import multiprocessing as mp

import nltk

from .lang_detect import detect as lang_detect
from .parser import parse_file
from .training.train import generate_ngrams
from . import is_news

import config


def _read_profile(lang, cat):
    with open(f'{config.PROFILE_DATA}/{lang}_{cat}.pickle', 'rb') as pf:
        return pickle.load(pf)


def load_cat_profiles():
    cat_profiles = {"en": [], "ru": []}
    for category in config.CATEGORIES:
        cat_profiles["en"].append(_read_profile("en", category))
        cat_profiles["ru"].append(_read_profile("ru", category))
    return cat_profiles


def cat_contents(contents, cat_profiles, raw_contents=None):
    lang = lang_detect(contents)
    if lang not in ["en", "ru"]:
        return None  # another language
    if raw_contents and not is_news.detect(raw_contents):
        return None
    ngrams = generate_ngrams(contents)
    guesses = {c: 0 for c in config.CATEGORIES}
    iter_cat = iter(config.CATEGORIES)
    for category in cat_profiles[lang]:
        guesses[next(iter_cat)] = nltk.jaccard_distance(ngrams, category)

    min_value = min(guesses, key=guesses.get)
    if guesses[min_value] > config.CATEGORIZATION_MAX_DISTANCE:
        guess = "other"
    else:
        guess = min_value
    return guess


def _cat_file(file_path, cat_profiles):
    with open(file_path, 'r') as f:
        raw_contents = f.read()
        contents = parse_file(raw_contents)

    return cat_contents(raw_contents, contents, cat_profiles)


def categorize(path):
    cat_profiles = load_cat_profiles()
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
    pool = mp.Pool(processes=8)
    for file in files:
        futures[file.split('/')[-1]] = pool.apply_async(_cat_file, (file, cat_profiles))
    pool.close()
    pool.join()

    for file in futures:
        guess = futures[file].get()
        if guess is None:
            continue
        result[result.index(next(i for i in result if i["category"] == guess))]["articles"].append(file)
    return result
