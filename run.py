import os
import sys
from libs.file import read_lines
from libs.tools import dt

path = os.path.dirname(__file__)
os.chdir(path)
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plagiat_clasterization.settings")

from main.models import News, NewsContent, NewsStemmed, NewsKeywords, Keyword

## create News and NewsContent
# news_path = 'd:/Vitalik/plagiat.giga/news'
# News.objects.load_from_folder(news_path)

## create NewsStemmed
# NewsContent.objects.create_stems()

## create NewsKeyword
# NewsStemmed.objects.create_keywords()

## create NewsStats
# NewsKeywords.objects.create_stats()

## gen_reports
# coefficients = [(1, 2), (1, 3), (1, 4)]
# for alpha, beta in coefficients:
#     print dt(), 'alpha=%.2f, beta=%.2f' % (alpha, beta)
#     NewsKeywords.objects.create_keywords(alpha, beta, gen_report=True)

## create keywords
# alpha = 10
# beta = 100
# NewsKeywords.objects.create_keywords(alpha, beta)

## load clustered doc_ids
doc_ids = read_lines('.conf/clustered.txt')
doc_ids = map(int, doc_ids)

## calculate cosinuses
Keyword.objects.calculate_cosinuses(doc_ids)
