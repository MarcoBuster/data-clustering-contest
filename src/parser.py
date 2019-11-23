import lxml.html as html_parser

import config
from . import lang_detect

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


def meta_tags(head):
    # TODO: Unused for now
    for meta in head.findall("meta"):
        attrib = meta.attrib
        if not attrib.get('property') or not attrib.get('content'):
            continue
        yield (attrib.get('property').split(':')[1], attrib.get('content'))


def ranking_score(html_root):
    _childrens = html_root.getchildren()
    head, body = _childrens[0], _childrens[1]
    article = body.getchildren()[0]
    words = len(article.text_content().split())
    paragraphs = article.findall("p")
    links = 0
    for p in paragraphs:
        hrefs = len(p.findall("a"))
        if hrefs > 0:
            links += hrefs
    figures = len(article.findall("figure"))
    return (words // 10) + (figures * 3) + (links * 1.5)


def news_score(title, lang):
    score = 0
    for word in title.split(' '):
        if word.lower() in NEWS_WORDS[lang]:
            score += 1.5
        if word.lower() in NOT_NEWS_WORDS[lang]:
            score -= 1
    return score > -1


def parse_file(filename, compute_ranking_score=False, compute_news_score=False):
    with open(filename, 'r') as f:
        raw_contents = f.read()
    html_root = html_parser.fromstring(raw_contents)
    _childrens = html_root.getchildren()
    head, body = _childrens[0], _childrens[1]
    article = body.getchildren()[0]
    title = article.text_content()
    """
    for metadata in meta_tags(head):
        print(metadata)

    _time = article.getchildren()[1].find("time")
    if _time:
        date_published = _time.attrib.get("datetime")
    else:
        date_published = "???"
    """
    contents = article.text_content()
    """
    print('[TITLE]', title)
    print('[DATE]', date_published)
    print('[TEXT]', body)
    """
    lang = lang_detect.detect(contents)
    return {
        'filename': filename.split('/')[-1],
        'title': title,
        'contents': contents,
        'lang': lang,
        'ranking_score': ranking_score(html_root) if lang in config.LANGUAGES and compute_ranking_score else None,
        'news_score': news_score(title, lang) if lang in ["en", ] and compute_news_score else None,
    }
