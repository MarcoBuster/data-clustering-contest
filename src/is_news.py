import glob

from . import parser


def detect(path):
    files = glob.glob(path + '*.html')
    result = {"articles": []}
    for file in files:
        parsed_file = parser.parse_file(file, compute_news_score=True)
        if parsed_file["news_score"]:
            result["articles"].append(parsed_file["filename"])
    return result
