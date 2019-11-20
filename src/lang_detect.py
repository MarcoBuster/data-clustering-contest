import langdetect


def detect(text):
    try:
        return langdetect.detect(text)
    except:
        return None
