I chose to use python 3 because it is very good at working with strings.
To parse the HTML I use a very light library (lxml), which returns the title and the text of the article. Given the high RAM capacity available and the importance of performance, throughout the process the file is opened only once and then is saved in RAM.
To categorize the text I generate for each HTML file its n-grams and compare them with the saved profiles [see training]; to divide the news into threads the program compares the n-grams between the files themselves: articles with a distance below a certain threshold are considered to belong to the same thread.
The software is modular and "hackable", it is easy to extend the code with other features.

Configuration
===========
In the root directory of the project there is a file called config.py; with it you can modify some parameters that impact performance and precision, without ever touching the code.
Read the comments in the file for more information about the individual fields.

Running in production
===================
The tgnews.sh script enters the virtualenv with each execution. I put this on to avoid having to install Python dependencies with pips, but you can only do this once: remove the "source ./venv/bin/activate" line in tgnews.sh after the first run.

Training
=======
I used two sources to train the category profiles:
- Wikinews articles (both EN and RU)
- This dataset on Kaggle https://www.kaggle.com/rmisra/news-category-dataset/data (only EN)

If you want to train your profiles with more data, here's how to do it:
- Install the optional dependencies by decommenting the packages at the bottom of python-requirements.txt and running "pip3 install -r requirements.txt".
- First enter the src/training/ folder; all operations and scripts are done here;
- All downloaded raw data goes to pretrain_data/, those merged with Telegram categories go to train_data/ and profiles are generated to profile_data/
- If you want to download from Wikinews, you can use the script wikinews_dw.py Opening it and modifying the main one you can program it to download more content together, by default it asks every time you want to download
- If you want to parade the Kaggle dataset linked above, use dataset_extract.py instead; it can take a long time but the quantity and quality of the extracted data is very good
- The train.py script trains all files in train_data/ and generates profiles in profile_data/. The size of the profiles should not be larger than a few dozen KBs.

Notes
=====
I can't say if the categorization in Russian is precise or not, because it's a language I don't know and it's too different from my mother tongue. The concept remains, just generate better profiles using the guide above.
Once the profiles are generated, the software can work with any other language, it is only necessary to modify the configuration file.