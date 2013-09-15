# coding: utf-8
import os
import sys
from libs.file import read_lines
from libs.logger import logger
from libs.timer import ts, tp
from libs.tools import dt

path = os.path.dirname(__file__)
os.chdir(path)
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plagiat_clasterization.settings")

from main.models import News, NewsContent, NewsParagraph, NewsStemmed, \
    NewsKeywords, ParagraphStemmed, ParagraphKeywords, NewsKeywordItem, \
    ParagraphKeywordItem, TitleStemmed, TitleKeywords, TitleKeywordItem

logger.debug('¶')


# stop_words = read_lines('.conf/stop_words.txt', 'cp1251')

## create NewsKeyword and ParagraphKeyword
# TitleStemmed.objects.create_keywords(stop_words, angry_mode=True)  # !!!
# NewsStemmed.objects.create_keywords(stop_words, angry_mode=True)
# ParagraphStemmed.objects.create_keywords(stop_words, angry_mode=True)

# create NewsStats and ParagraphStats
# NewsKeywords.objects.create_stats()
# ParagraphKeywords.objects.create_stats()

## gen_reports
# coefficients =  [(0, 100)]
# for alpha, beta in coefficients:
#     print dt(), 'alpha=%.2f, beta=%.2f' % (alpha, beta)
#     NewsKeywords.objects.create_keyword_items(alpha, beta, gen_report=True)


ts('build doc-news dependencies')
docs = dict()
news_by_docs = dict()
for news in News.objects.only('doc_id'):
    docs[news.pk] = news.doc_id
    news_by_docs[news.doc_id] = news.pk
tp()

# get 704 news
ts('load clustered news (704)')
several_doc_ids = read_lines('.conf/clustered.txt')  # load clustered several_doc_ids
several_doc_ids = map(int, several_doc_ids)
several_news_ids = []
if several_doc_ids and news_by_docs:
    several_doc_ids = set(several_doc_ids)
    for doc_id in several_doc_ids:
        several_news_ids.append(news_by_docs[doc_id])
tp()

# ts('load paragraph ids')
# items = NewsParagraph.objects.filter(news__in=several_news_ids).only('news')
# # paragraphs_by_news = dict()
# news_by_paragraph = dict()
# all_paragraphs = list()
# for item in items:
#     # print item.pk, item.news.pk
#     # paragraphs_by_news.setdefault(item.news.pk, list())
#     # paragraphs_by_news[item.news.pk].append(item.pk)
#     news_by_paragraph[item.pk] = item.news_id
#     all_paragraphs.append(item.pk)
# tp()
#
ts('load news keywords')
items = NewsKeywordItem.objects.filter(base__in=several_news_ids).\
    only('word', 'base')
ts('query')
items = list(items)
tp()
valid_keywords = dict()
for item in items:
    news_id = item.base_id
    valid_keywords.setdefault(news_id, list())
    valid_keywords[news_id].append(item.word)
tp()

ts('load title keywords')
items = TitleKeywordItem.objects.filter(base__in=several_news_ids).only('word',
                                                                        'base')
ts('query')
items = list(items)
tp()
title_keywords = dict()
for item in items:
    news_id = item.base_id
    title_keywords.setdefault(news_id, list())
    title_keywords[news_id].append(item.word)
tp()

## create NewsKeywordItem and ParagraphKeywordItem
alpha = 0
beta = 100
# TitleKeywords.objects.create_keyword_items()
# TitleKeywords.objects.create_keyword_items(several_news_ids)
NewsKeywords.objects.create_keyword_items(alpha, beta, several_news_ids,
                                          title_keywords)
# ParagraphKeywords.objects.create_keyword_items(all_paragraphs, news_by_paragraph, valid_keywords)

# todo: third mode: all news that intersects with 704

## calculate cosinuses for news
# NewsKeywordItem.objects.news_calculate_cosinuses(docs, news_by_docs,
#                                                  several_doc_ids)
# NewsKeywordItem.objects.news_calculate_cosinuses(docs, news_by_docs)

## calculate cosinuses for paragraphs
# docs = dict()
# for news in News.objects.only('doc_id'):
#     docs[news.pk] = news.doc_id
# ParagraphKeywordItem.objects.paragraph_calculate_cosinuses(docs, 0.7)
# ParagraphKeywordItem.objects.paragraph_calculate_cosinuses(docs, 1, several=False)

# todo: calc all cosinuses and then try to check different coefficient "d"

# just for fun :)
