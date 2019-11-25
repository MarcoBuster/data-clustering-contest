from . import common
from .modules import lang_detect, is_news, categorization, news_threads, ranking


def language(path):
    results = lang_detect.process(path)
    common.print_json(results)


def news(path):
    results = is_news.process(path)
    common.print_json(results)


def categories(path):
    results = categorization.process(path)
    common.print_json(results)


def threads(path):
    results = news_threads.process(path)
    common.print_json(results)


def top(path):
    results = ranking.process(path)
    common.print_json(results)
