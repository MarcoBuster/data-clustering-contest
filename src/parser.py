import lxml.html as html_parser
from . import lang_detect


def meta_tags(head):
    for meta in head.findall("meta"):
        attrib = meta.attrib
        if not attrib.get('property') or not attrib.get('content'):
            continue
        yield (attrib.get('property').split(':')[1], attrib.get('content'))


def get_title_and_summary(contents):
    root = html_parser.fromstring(contents)
    _childrens = root.getchildren()
    head, body = _childrens[0], _childrens[1]
    article = body.getchildren()[0]
    title = article.find("h1").text
    body = article.text_content()
    return title, ' '.join(body.split()[:20])


def ranking_score(contents):
    root = html_parser.fromstring(contents)
    _childrens = root.getchildren()
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


def parse_file(filename):
    with open(filename, 'r') as f:
        raw_contents = f.read()
    root = html_parser.fromstring(raw_contents)
    _childrens = root.getchildren()
    head, body = _childrens[0], _childrens[1]
    article = body.getchildren()[0]
    title = article.find("h1").text
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
    return {
        'filename': filename.split('/')[-1],
        'title': title,
        'contents': contents,
        'lang': lang_detect.detect(contents),
    }
