from . import common, lang_detect, is_news, categorization, news_threads, ranking


def language(path):
    results = lang_detect.process(path)
    common.print_json(results)


def news(path):
    results = is_news.detect(path)
    common.print_json(results)


def categories(path):
    results = categorization.categorize(path)
    common.print_json(results)


def threads(path):
    results = news_threads.generate_threads(path)
    common.print_json(results)


def top(path):
    results = ranking.rank_threads(path)
    common.print_json(results)
