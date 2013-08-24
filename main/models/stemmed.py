# coding: utf-8
import re
from django.db import models
from libs.manager import LargeManager
from libs.tools import dt
from main.models import NewsKeywords
from main.models.news import News


class CreateStemmedManager(LargeManager):
    stemmed_model = NewsStemmed

    def create_stems(self):
        print dt(), '@ Creating stems of news'
        i = 0
        items = []
        for news in self.iterate():
            i += 1
            if not i % 100:
                print dt(), '-> processed:', i
            stemmed = news.create_stemmed()
            items.append(stemmed)
        print dt(), '@ Adding stems of DB'
        self.bulk(items, model=self.stemmed_model, chunk_size=50)


class NewsStemmedManager(LargeManager):
    def create_keywords(self):
        print dt(), '@ Extract list of valid keywords from stemmed data'
        i = 0
        items = []
        for news in self.iterate(100):
            i += 1
            # if i > 500:
            #     break
            if not i % 500:
                print dt(), '-> processed:', i
            news_keyword = news.create_keywords()
            items.append(news_keyword)
        print dt(), '@ Adding news_keywords to DB'
        self.bulk(items, model=NewsKeywords, chunk_size=250)


class NewsStemmed(models.Model):
    news = models.ForeignKey(News)
    stemmed = models.TextField(blank=True)

    objects = NewsStemmedManager()

    def create_keywords(self):
        # print self.news_id
        lines = self.stemmed.split('\n')
        keywords = []
        for line in lines:
            # print line
            m = re.match('(.*)\{(.*)\}', line)
            stem = m.group(2)
            items = stem.split('|')
            forms = []
            for item in items:
                try:
                    # print item
                    word, word_type = item.split('=')
                except ValueError:
                    word, word_type = item, '?'
                # print word_type
                if word_type in ['S', 'V', 'A', 'ADV']:
                    forms.append(word)
                    break  # use only first form
            for word in set(forms):
                keywords.append(word)
        # print keywords
        keywords = ' '.join(keywords)
        return NewsKeywords(news=self.news, keywords=keywords)
