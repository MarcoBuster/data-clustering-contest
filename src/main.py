from . import parser, common, is_news, categorization, news_threads, ranking
import config


def language(path):
    results = [{"lang_code": l, "articles": []} for l in config.LANGUAGES]
    files = common.get_files(path)
    for file in files:
        parsed_file = parser.parse_file(file)
        if parsed_file["lang"] not in config.LANGUAGES:
            continue
        results[config.LANGUAGES.index(parsed_file["lang"])]["articles"].append(parsed_file["filename"])
    common.print_json(results)


def news(path):
    results = is_news.detect(path)
    common.print_json(results)


def categories(path):
    results = categorization.categorize(path)
    common.print_json(results)


def threads(path):
    results = news_threads.split_in_threads(path)
    common.print_json(results)


def top(path):
    results = ranking.rank_threads(path)
    common.print_json(results)
