from . import parser, common, lang_detect

ACCEPTABLE_LANGUAGES = [
    "en",
    "ru"
]


def language(path):
    results = [{"lang_code": l, "articles": []} for l in ACCEPTABLE_LANGUAGES]
    files = common.get_files(path)
    for file in files:
        body = parser.parse_file(common.read_file(file))
        lang = lang_detect.detect(body)
        if lang not in ACCEPTABLE_LANGUAGES:
            continue
        results[ACCEPTABLE_LANGUAGES.index(lang)]["articles"].append(file)

    print(f'READ: {len(files)}')
    common.print_json(results)
