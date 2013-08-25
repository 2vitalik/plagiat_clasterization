import os
import sys
from libs.file import read_lines
from libs.tools import dt

path = os.path.dirname(__file__)
os.chdir(path)
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plagiat_clasterization.settings")

from main.models import News, NewsContent, NewsParagraph, NewsStemmed, \
    NewsKeywords, ParagraphStemmed, ParagraphKeywords, NewsKeywordItem

## create News and NewsContent
# news_path = 'd:/www/giga/plagiat/news'
# News.objects.load_from_folder(news_path)

## create NewsParagraph
# NewsContent.objects.create_paragraphs()

## create NewsStemmed and ParagraphStemmed
# NewsContent.objects.create_stems()
# NewsParagraph.objects.create_stems()

## create NewsKeyword and ParagraphKeyword
# NewsStemmed.objects.create_keywords()
# ParagraphStemmed.objects.create_keywords()

# create NewsStats and ParagraphStats
# NewsKeywords.objects.create_stats()
# ParagraphKeywords.objects.create_stats()

## gen_reports
# coefficients = [(1, 2), (1, 3), (1, 4)]
# for alpha, beta in coefficients:
#     print dt(), 'alpha=%.2f, beta=%.2f' % (alpha, beta)
#     NewsKeywords.objects.create_keyword_items(alpha, beta, gen_report=True)

## create NewsKeywordItem and ParagraphKeywordItem
# alpha = 10
# beta = 100
# NewsKeywords.objects.create_keyword_items(alpha, beta)
# ParagraphKeywords.objects.create_keyword_items(alpha, beta)

## load clustered doc_ids
doc_ids = read_lines('.conf/clustered.txt')
doc_ids = map(int, doc_ids)

## calculate cosinuses
docs = dict()
news_docs = dict()
for news in News.objects.only('doc_id'):
    docs[news.pk] = news.doc_id
    news_docs[news.doc_id] = news.pk
NewsKeywordItem.objects.calculate_cosinuses(docs, news_docs, doc_ids)
# Keyword.objects.calculate_cosinuses()
