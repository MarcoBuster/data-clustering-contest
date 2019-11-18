import langdetect
from . import common


def detect(text):
    try:
        return langdetect.detect(text)
    except:
        return None

