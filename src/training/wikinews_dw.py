import bs4
import requests
from wikipedia import wikipedia
import urllib.parse


def scrape_urls_from_category(lang, category):
    base_url = f'https://{lang}.wikinews.org'
    next_page = f'/w/index.php?title={"Category" if lang == "en" else "Категория"}:{category}&subcatfrom=0&filefrom=0'
    urls = []
    while True:
        r = requests.get(base_url + next_page)

        soup = bs4.BeautifulSoup(r.text, "html.parser")
        content = soup.findAll("div", {"class": "mw-content-ltr"})
        articles = content[-1]
        links = articles.findAll("a")
        for link in links:
            url = link.get('href')
            print(url)
            if ('Wikinews:' if lang == "en" else "Викиновости") in url:
                continue
            urls.append(url)

        next_page_btn = soup.find(id='mw-pages').findAll('a')[-1]
        if ('previous' if lang == "en" else "Предыдущая") in next_page_btn.text:
            break
        next_page = next_page_btn.get('href')
    return urls


def get_text_from_url(lang, location):
    wikipedia.API_URL = f'https://{lang}.wikinews.org/w/api.php'
    parsed = urllib.parse.unquote(location.lstrip("/wiki/"))
    p = wikipedia.WikipediaPage(parsed)
    return '\n'.join(p.summary.split('\n')[1:]).replace('\n', '').rstrip().lstrip()


def generate_category_file(lang, category):
    with open(f'pretrain_data/{lang}_{category.lower()}.txt', 'a+') as f:
        results = scrape_urls_from_category(lang, category)
        print(f'Found {len(results)} for {category}-{lang} category.')
        i = 0
        for url in results:
            r = get_text_from_url(lang, url)
            length = f.write(r)
            print(f'[{i}/{len(results)} - {round(i / len(results) * 100, 2)}%] Wrote {length} bytes.')
            i += 1


if __name__ == "__main__":
    language = input("Which language do you want ? [en/ru]: ")
    cat = input("Which category do you want to download?: ")
    generate_category_file(language, cat)
