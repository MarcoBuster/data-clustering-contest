import lxml.html as html_parser
import config
import glob
from . import parser, lang_detect


NEWS_WORDS = {
    "en": [
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
    ],
}
NOT_NEWS_WORDS = {
    "en": [
        "top",
        "how to",
        "best",
        "gift", "gifts",
        "best",
        "your",
    ]
}


def compute_score(contents, lang):
    score = 0

    root = html_parser.fromstring(contents)
    _childrens = root.getchildren()
    head, body = _childrens[0], _childrens[1]
    article = body.getchildren()[0]
    title = article.find("h1").text

    for word in title.split(' '):
        if word.lower() in NEWS_WORDS[lang]:
            score += 1.5
        if word.lower() in NOT_NEWS_WORDS[lang]:
            score -= 1
    words = article.text_content().split()
    return score > -1


def detect(path):
    files = glob.glob(path + '*.html')
    result = {"articles": []}
    for file in files:
        with open(file, "r") as f:
            contents = f.read()
        lang = lang_detect.detect(parser.parse_file(contents))
        if lang not in ["en", ]:
            continue

        if compute_score(contents, lang):
            result["articles"].append(file.split('/')[-1])
    return result
