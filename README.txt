Introduction
============
I chose to use Python 3 because I find it very useful when working with strings and large dicts; the performance is enough.
To parse the HTML I use a very light library (lxml), which returns the title and the text of the article. Given the high RAM capacity available and the importance of performance, throughout the process the file is opened only once and then is saved in RAM.
To categorize the text I generate n-grams[1] for each HTML file and compare them with the saved profiles [see training]; to divide the news into threads the program compares the n-grams between the files themselves: articles with a distance below a certain threshold are considered to belong to the same thread.
The software uses the multiprocessing feature, and with it the software operates by default with slow operations with 8 processes at time (the number of CPU cores). You can change this value in the configuration file.

I wrote this project as modular as possible (without sacrificing speed), and it is easy to extend the code with other features.


Configuration
=============
In the root directory of the project there is a file called config.py; with it you can modify some parameters that will impact on performance and precision, without even touching the code.
Read the comments in the file for more information about the individual fields.


Running in production
=====================
The tgnews script enters in the Python virtualenv at every execution.
I put this to avoid having to install Python dependencies with pip, but you can only do this once: remove the "source ./venv/bin/activate" line in tgnews after the first run.
You can install the dependencies system-wide without the need of virtualenvs by running:
$ sudo python3 -m pip install -r python-requirements.txt


Profile training
================
I used two sources to train the category profiles:
- Wikinews articles (both EN and RU)
- This dataset on Kaggle https://www.kaggle.com/rmisra/news-category-dataset/data (only EN)

If you want to train your profiles with more data, here's how to do it:
- Install the optional dependencies by decommenting the packages at the bottom of python-requirements.txt and running "sudo python3 -m pip install -r python-requirements.txt".
- Enter in the src/training/ folder; all operations and scripts are meant to be executed here;
- All downloaded raw data goes to pretrain_data/, those merged with Telegram categories go to train_data/ and profiles are generated in profile_data/
- If you want to download from Wikinews, you can use the wikinews_dw.py script. By default it asks every time what you want to download, by if you open it you can hack the main function to download more content together.
- If you want to train the Kaggle dataset linked above, use dataset_extract.py instead; it can take a long time but the quantity and quality of the extracted data is better.
- The train.py script trains all the files in train_data/ and generates profiles in profile_data/. The size of the profiles should not be larger than a few dozen KBs. Those profiles are used by the software.


Notes
=====
I can't tell if whether the categorization in Russian is precise or not, because it's a language that I don't understand. The concept is the same, and
if it's not very good you can generate better profiles using the guide above.
Once the profiles are generated, the software can work with any other language, it is only necessary to edit the configuration file.


References
==========
[1]: N-Gram-Based Text Categorization by William B. Cavnar and John M. Trenkle - http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.21.3248&rep=rep1&type=pdf
