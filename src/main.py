from . import parser, common, lang_detect, categorization, news_threads
import config


def language(path):
    results = [{"lang_code": l, "articles": []} for l in config.LANGUAGES]
    files = common.get_files(path)
    for file in files:
        body = parser.parse_file(common.read_file(file))
        lang = lang_detect.detect(body)
        if lang not in config.LANGUAGES:
            continue
        results[config.LANGUAGES.index(lang)]["articles"].append(file.split('/')[-1])
    common.print_json(results)


def categories(path):
    results = categorization.categorize(path)
    common.print_json(results)


def threads(path):
    results = news_threads.split_in_threads(path)
    common.print_json(results)
