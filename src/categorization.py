import pickle
import nltk
from .training.train import generate_ngrams
from .parser import parse_file
from .lang_detect import detect as lang_detect
import glob
import json
import time


CATEGORIES = ["economy", "entertainment", "society", "sports"]
PROFILE_DATA = "src/training/profile_data"


def _read_profile(lang, cat):
    with open(f'{PROFILE_DATA}/{lang}_{cat}.pickle', 'rb') as pf:
        return pickle.load(pf)


def _calculate_distance(file, cat_profile):
    with open(file, "r") as f:
        file_ngrams = generate_ngrams(f.read())
        nltk.jaccard_distance(cat_profile, file_ngrams)


def categorize(path):
    cat_profiles = []
    for category in CATEGORIES:
        cat_profiles.append(_read_profile("en", category))

    result = dict.fromkeys(CATEGORIES, [])
    result['other'] = []
    for file in glob.glob(path + '*.html'):
        with open(file, 'r') as f:
            contents = parse_file(f.read())
            if lang_detect(contents) != 'en':
                continue

            ngrams = generate_ngrams(contents)
            guesses = {c: 0 for c in CATEGORIES}
            iter_cat = iter(CATEGORIES)
            for category in cat_profiles:
                guesses[next(iter_cat)] = nltk.jaccard_distance(ngrams, category)

            min_value = min(guesses, key=guesses.get)
            if guesses[min_value] > 0.96:
                guess = "other"
            else:
                guess = min_value
            result[guess].append(file.split('/')[-1])

    formatted_result = []
    for cat in [*CATEGORIES, "other"]:
        formatted_result.append({
            "category": cat,
            "articles": result[cat],
        })
    return formatted_result
