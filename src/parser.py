import lxml.html as html_parser

import config
from .training import train
import nltk
import pickle

NEWS_WORDS = [
    "news",
    "breaking",
    "breaking news",
    "today",
    "yesterday"
    "this evening",
    "this afternoon",
    "happened",
    "why",
    "rescued",
    "player", "players",
    "announced",
    "известие",
    "разрывной",
    "последние новости",
    "сегодня",
    "вчера",
    "этот вечер",
    "сегодня днем",
    "произошедший",
    "зачем",
    "спасённый",
    "проигрыватель", "проигрыватели",
    "анонсированный",
]

NOT_NEWS_WORDS = [
    "top",
    "how to",
    "best",
    "gift", "gifts",
    "best",
    "your",
    "here are my", "here is my",
    "my favourite",
    "известие",
    "как",
    "лучший",
    "дар", "подарки",
    "лучший",
    "твой",
    "вот мой", "вот мой",
    "мой любимый",
]


def generate_parsed_file(filename, *args, **kwargs):
    # This is needed in multiprocessing functions
    return ParsedFile(filename, *args, **kwargs)


class ParsedFile:
    # Load the profiles
    _language_profiles = {}
    _cat_profiles = dict((l, dict()) for l in config.LANGUAGES)
    for lang in config.LANGUAGES:
        with open(config.PROFILE_DATA + '/' + lang + '.pickle', 'rb') as f:
            _language_profiles[lang] = pickle.load(f)

        for cat in config.CATEGORIES:
            with open(f"{config.PROFILE_DATA}/{lang}_{cat}.pickle", 'rb') as cf:
                _cat_profiles[lang][cat] = pickle.load(cf)

    def __init__(self, filename, pre_compute=()):
        self._filename = filename
        self.filename = self._filename.split('/')[-1]

        self.raw_contents = None
        self.contents = None
        self.title = None

        self._article = None
        self._ngrams = None
        self._short_ngrams = None
        self._stopwords_ngrams = None
        self._lang = None
        self._category = None
        self._ranking_score = None
        self._news_score = None

        # Open and parse the file
        with open(self._filename, 'r') as f:
            self.raw_contents = f.read()
        html_root = html_parser.fromstring(self.raw_contents)
        _children = html_root.getchildren()
        _, body = _children[0], _children[1]
        _article = body.getchildren()[0]
        self.title = _article.xpath('normalize-space(//h1)')
        self.contents = _article.text_content()
        self._stopwords_ngrams = None

        # Pre compute statements
        if 'lang' in pre_compute:
            self.lang()
        if 'category' in pre_compute:
            self.category()
        if 'ranking_score' in pre_compute:
            self.ranking_score()
        if 'news_score' in pre_compute:
            self.news_score()
        if 'short_ngrams' in pre_compute:
            self.short_ngrams()

    def lang(self):
        if self._lang is not None:
            return self._lang

        stopwords_ngrams = self.stopwords_ngrams()
        guesses = dict.fromkeys(config.LANGUAGES)
        for lang in guesses:
            guesses[lang] = nltk.jaccard_distance(stopwords_ngrams, ParsedFile._language_profiles[lang])
        best_guess = min(guesses, key=guesses.get)

        if guesses[best_guess] > config.LANGUAGE_MAX_DISTANCE:
            best_guess = "other"
        self._lang = best_guess
        return self._lang

    def category(self):
        if self._category is not None:
            return self._category
        if self.lang() not in config.LANGUAGES or not self.news_score():
            self._category = 0
            return self._category

        guesses = {c: 0 for c in config.CATEGORIES}
        iter_cat = iter(config.CATEGORIES)
        for category in ParsedFile._cat_profiles[self.lang()]:
            guesses[next(iter_cat)] = nltk.jaccard_distance(self.ngrams(), ParsedFile._cat_profiles[self.lang()][category])

        min_value = min(guesses, key=guesses.get)
        if guesses[min_value] > config.CATEGORIZATION_MAX_DISTANCE:
            self._category = "other"
        else:
            self._category = min_value
        return self._category

    def ranking_score(self):
        if self._ranking_score is not None:
            return self._ranking_score
        if self.lang() not in config.LANGUAGES or not self.news_score():
            self._ranking_score = 0
            return self._ranking_score

        html_root = html_parser.fromstring(self.raw_contents)
        _children = html_root.getchildren()
        _, body = _children[0], _children[1]
        _article = body.getchildren()[0]
        words = len(_article.text_content().split())
        paragraphs = _article.findall("p")
        links = 0
        for p in paragraphs:
            hrefs = len(p.findall("a"))
            if hrefs > 0:
                links += hrefs
        figures = len(_article.findall("figure"))
        _ranking_score = (words // 10) + (figures * 3) + (links * 1.5)
        return _ranking_score

    def news_score(self):
        if self._news_score is not None:
            return self._news_score
        if self.lang() not in config.LANGUAGES:
            self._news_score = 0
            return self._news_score

        score = 0
        for word in self.title.split(' '):
            if word.lower() in NEWS_WORDS:
                score += 1.5
            if word.lower() in NOT_NEWS_WORDS:
                score -= 1
        self._news_score = score > -1
        return self._news_score

    def ngrams(self):
        if self._ngrams is not None:
            return self._ngrams

        self._ngrams = train.generate_ngrams(self.contents)
        return self._ngrams

    def short_ngrams(self):
        if self._short_ngrams is not None:
            return self._short_ngrams
        if self.lang() not in config.LANGUAGES or not self.news_score():
            self._short_ngrams = {}
            return self._short_ngrams

        ngram_string = self.title + ' '.join(self.contents.split()[:20])
        self._short_ngrams = train.generate_ngrams(ngram_string, 3)
        return self._short_ngrams

    def stopwords_ngrams(self):
        if self._stopwords_ngrams is not None:
            return self._stopwords_ngrams

        self._stopwords_ngrams = train.generate_ngrams(self.contents, maximum=1, only_stopwords=True)
        return self._stopwords_ngrams
