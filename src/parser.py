import lxml.html as html_parser

import config
from .modules import lang_detect
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
]

NOT_NEWS_WORDS = [
    "top",
    "how to",
    "best",
    "gift", "gifts",
    "best",
    "your",
    "известие",
    "как",
    "лучший",
    "дар", "подарки",
    "лучший",
    "твой",
]


def generate_parsed_file(filename, *args, **kwargs):
    # This is need in multiprocessing functions
    return ParsedFile(filename, *args, **kwargs)


class ParsedFile:
    _language_profiles = {}
    for lang in config.LANGUAGES:
        with open(config.PROFILE_DATA + '/' + lang + '.pickle', 'rb') as f:
            _language_profiles[lang] = pickle.load(f)

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
        self._ranking_score = None
        self._news_score = None

        with open(self._filename, 'r') as f:
            self.raw_contents = f.read()
        html_root = html_parser.fromstring(self.raw_contents)
        _childrens = html_root.getchildren()
        _, body = _childrens[0], _childrens[1]
        _article = body.getchildren()[0]
        self.title = _article.xpath('normalize-space(//h1)')
        self.contents = _article.text_content()
        self._stopwords_ngrams = None

        if 'lang' in pre_compute:
            self.lang()
        if 'ranking_score' in pre_compute:
            self.ranking_score()
        if 'news_score' in pre_compute:
            self.news_score()
        if 'ngrams' in pre_compute:
            self.ngrams()
        if 'short_ngrams' in pre_compute:
            self.short_ngrams()
        if 'stopwords_ngrams' in pre_compute:
            self.stopwords_ngrams()

    def lang(self):
        if self._lang:
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

    def ranking_score(self):
        if self._ranking_score is not None:
            return self._ranking_score

        html_root = html_parser.fromstring(self.raw_contents)
        _childrens = html_root.getchildren()
        _, body = _childrens[0], _childrens[1]
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

        ngram_string = self.title + ' '.join(self.contents.split()[:20])
        self._short_ngrams = train.generate_ngrams(ngram_string, 3)
        return self._short_ngrams

    def stopwords_ngrams(self):
        if self._stopwords_ngrams is not None:
            return self._stopwords_ngrams

        self._stopwords_ngrams = train.generate_ngrams(self.contents, maximum=1, only_stopwords=True)
        return self._stopwords_ngrams
