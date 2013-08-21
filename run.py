import os
import sys

path = os.path.dirname(__file__)
os.chdir(path)
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plagiat_clasterization.settings")

from main.models import News, NewsContent

# create News and NewsContent
# news_path = 'd:/Vitalik/plagiat.giga/news'
# News.objects.load_from_folder(news_path)

# create NewsStemmed
NewsContent.objects.create_stems()

# create NewsKeyword
# News.objects.process_keywords()

# create Keyword
# News.objects.calc_keywords()
