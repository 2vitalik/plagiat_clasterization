# coding: utf-8
import os
import sys

path = os.path.dirname(__file__)
os.chdir(path)
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "plagiat_clasterization.settings")

from main.steps import MissedValueError, Steps
from main.models import News, NewsContent, NewsParagraph, NewsStemmed, \
    NewsKeywords, ParagraphStemmed, ParagraphKeywords, NewsKeywordItem, \
    ParagraphKeywordItem, TitleStemmed, TitleKeywords, TitleKeywordItem

# todo: third mode: all news that intersects with 704
# todo: calc all cosinuses and then try to check different coefficient "d"

app = Steps()
app.build_docs_news_dependencies()
app.calculate_paragraph_cos()
