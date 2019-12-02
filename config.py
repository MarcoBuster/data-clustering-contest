# Configuration file with some parameters.
# You can play with these to increase performance or accuracy;
# default values should be ok for
# "Debian GNU/Linux 10.1 (buster), x86-64 with 8 cores and 16 GB RAM".

# Number of concurrent processes used for slow operations
CONCURRENT_PROCESSES = 8

# Path to profiles
PROFILE_DATA = "src/training/profile_data"

# Allowed categories. These values are taken from contest docs.
# Remember that you need to have profiles for all categories in all languages
# to use them.
CATEGORIES = ["economy", "entertainment", "society", "sports", "science", "technology"]

# Allowed languages. These values are taken from contest docs.
LANGUAGES = ["en", "ru"]

# Max ngrams to generate per file (either for training or not)
MAX_NGRAMS = 350

# Max jaccard distance for considering an article written in a language
LANGUAGE_MAX_DISTANCE = 0.87

# Max jaccard distance for considering an article in a category
CATEGORIZATION_MAX_DISTANCE = 0.95

# Max jaccard distance for considering two articles in the same thread
THREADING_MAX_DISTANCE = 0.93
