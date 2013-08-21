import os
import sys
from libs.tools import dt

path = os.path.dirname(__file__)
os.chdir(path)
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plagiat_clasterization.settings")

from main.models import News, NewsContent, NewsStemmed, NewsKeywords

# create News and NewsContent
# news_path = 'd:/Vitalik/plagiat.giga/news'
# News.objects.load_from_folder(news_path)

# create NewsStemmed
# NewsContent.objects.create_stems()

# create NewsKeyword
# NewsStemmed.objects.create_keywords()

# create NewsStats
# NewsKeywords.objects.create_stats()

# create Keyword
coefficients = [(1, 2), (1, 3), (1, 4)]
for alpha, beta in coefficients:
    print dt(), 'alpha=%.2f, beta=%.2f' % (alpha, beta)
    NewsKeywords.objects.create_keywords(alpha, beta, gen_report=True)
