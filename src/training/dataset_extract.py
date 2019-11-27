import json


BIND_CATEGORIES = {
    "CRIME": "society",
    "ENTERTAINMENT": "entertainment",
    "WORLD NEWS": "society",
    "IMPACT": None,
    "POLITICS": "society",
    "WEIRD NEWS": None,
    "BLACK VOICES": "society",
    "WOMEN": "society",
    "COMEDY": "entertainment",
    "QUEER VOICES": "society",
    "SPORTS": "sports",
    "BUSINESS": "economy",
    "TRAVEL": None,
    "MEDIA": "society",
    "TECH": "technology",
    "RELIGION": "society",
    "SCIENCE": "science",
    "LATINO VOICES": "society",
    "EDUCATION": "society",
    "COLLEGE": "society",
    "PARENTS": None,
    "ARTS & CULTURE": None,
    "STYLE": None,
    "GREEN": None,
    "TASTE": None,
    "HEALTHY LIVING": None,
    "THE WORLDPOST": None,
    "GOOD NEWS": None,
    "WORLDPOST": None,
    "FIFTY": None,
    "ARTS": None,
    "WELLNESS": None,
    "PARENTING": None,
    "HOME & LIVING": None,
    "STYLE & BEAUTY": None,
    "DIVORCE": "society",
    "WEDDINGS": None,
    "FOOD & DRINK": None,
    "MONEY": None,
    "ENVIRONMENT": "society",
    "CULTURE & ARTS": None,
}


def read_file(path):
    categories = {
        'economy': None,
        'society': None,
        'sports': None,
        'technology': None,
        'science': None,
        'entertainment': None,
        'other': None
    }
    for cat in categories:
        categories[cat] = open(f'train_data/en_{cat}.txt', 'a')

    with open(path, 'r') as f:
        i = 0
        total = 200853
        while True:
            line = f.readline()
            try:
                article = json.loads(line)
                cat = BIND_CATEGORIES.get(article["category"])
                if cat is None:
                    cat = "other"
                categories[cat].write(f'\n{article["headline"]}\n{article["short_description"]}')
                i += 1
                print(f'Read/Wrote {i}/{total} ({round(i/total, 4)*100}%)')
            except json.decoder.JSONDecodeError:
                break
    return categories


if __name__ == "__main__":
    print('Please download the dataset from https://www.kaggle.com/rmisra/news-category-dataset/data;')
    print('Extract the zip file and put News_Category_Dataset_v2.json in pretrain_data/')
    input('Press any key to continue...')
    read_file('pretrain_data/News_Category_Dataset_v2.json')
