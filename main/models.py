# coding: utf-8
import os
import re
import gc
import time
from collections import Counter
from datetime import datetime
from django.db import models
from xml.etree import ElementTree
from libs.mystem import mystem
from libs.tools import w2u, chunks, dt
from libs.xmath import average_deviation, alpha_beta


class LargeManager(models.Manager):
    def iterate(self, chunksize=1000):
        pk = 0
        last_pk = self.order_by('-pk')[0].pk
        queryset = self.order_by('pk')
        while pk < last_pk:
            for row in queryset.filter(pk__gt=pk)[:chunksize]:
                pk = row.pk
                yield row
            gc.collect()


class NewsManager(LargeManager):
    def load_from_folder(self, news_path):
        print dt(), '§ Loading files, adding news to DB, creating news_contests'
        files = os.listdir(news_path)
        items = []
        i = 0
        for filename in files:
            i += 1
            if not i % 500:
                print dt(), '→ processed:', i
            news_content = \
                self.load_from_xml("{}/{}".format(news_path, filename))
            items.append(news_content)
        print dt(), '→ Total entries:', len(items)
        print dt(), '§ Adding news_contests to DB'
        chunk_size = 250
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(NewsContent.objects.bulk_create(chunk))
            print '→ Processed:', processed

    def load_from_xml(self, filename):
        def fix_xml(text):
            text = "<root>{}</root>".format(text)
            text = text.replace('&', '&amp;')
            text = text.replace('<p>', '\n')
            text = text.replace('<>', ' ')
            return w2u(text)
        # print '→ Processing file:', filename
        text = open(filename).read()
        tree = ElementTree.fromstring(fix_xml(text))
        data = {}
        for child in tree:
            name = child.tag
            value = child.text.strip()
            # print "[{}]=[{}]".format(child.tag, value.encode('utf-8'))
            data[name] = value
        doc_id = int(data['docID'][8:])
        news = News(doc_id=doc_id, url=data['docURL'],
                    subject=data['subject'], agency=data['agency'],
                    date=data['date'], daytime=data['daytime'])
        news.save()
        news_content = NewsContent(news=news, content=data['content'])
        return news_content


class News(models.Model):
    doc_id = models.IntegerField()
    url = models.URLField()
    subject = models.CharField(max_length=500)
    agency = models.CharField(max_length=100)
    date = models.IntegerField()
    daytime = models.IntegerField()
    content = models.TextField()
    stemmed = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

    objects = NewsManager()


class NewsContentManager(LargeManager):
    def create_stems(self):
        print dt(), '§ Creating stems of news'
        i = 0
        items = []
        for news in self.iterate():
            i += 1
            if not i % 100:
                print dt(), '→ processed:', i
            stemmed = news.create_stemmed()
            items.append(stemmed)
        print dt(), '§ Adding stems of DB'
        chunk_size = 10
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(NewsStemmed.objects.bulk_create(chunk))
            print dt(), '→ Processed:', processed


class NewsContent(models.Model):
    news = models.ForeignKey(News)
    content = models.TextField()

    objects = NewsContentManager()

    def stem(self):
        return mystem(self.content)

    def create_stemmed(self):
        # print dt(), self.news_id
        stem = self.stem()
        stemmed = []
        lines = re.split('[\r\n]', stem)
        lines = filter(str.strip, lines)  # удаление пустых строк
        for line in lines:
            word = line.strip()
            if re.search(r'\\n|\\r|[_":;]', word):
                # if re.search('[{}]', word):
                #     print word
                continue
            if len(word) < 5:
                continue
            if re.search('.*\{.*\}', word) and not re.match('(.*)\{(.*)\}', word):
                print '?', word
            if not re.search('.*\{.*\}', word):
                # print 'x', word
                continue
            # word = re.sub('\(.*?\)', '', word)
            # word = re.sub('=[^=]*?([|}])', '\\1', word)
            # word = re.sub(',[^=]*?([|}])', '\\1', word)
            stemmed.append(word)
        return NewsStemmed(news=self.news, stemmed='\n'.join(stemmed))


class NewsStemmedManager(LargeManager):
    def create_keywords(self):
        print dt(), '§ Extract list of valid keywords from stemmed data'
        i = 0
        items = []
        for news in self.iterate(100):
            i += 1
            if not i % 500:
                print dt(), '→ processed:', i
            news_keyword = news.create_keywords()
            items.append(news_keyword)
        print dt(), '§ Adding news_keywords to DB'
        chunk_size = 500
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(NewsStemmed.objects.bulk_create(chunk))
            print '→ Processed:', processed


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
                    word, word_type = item.split('=')
                except ValueError:
                    word, word_type = item, '?'
                if word_type in ['S', 'V', 'A', 'ADV']:
                    forms.append(word)
                    break  # use only first form
            for word in set(forms):
                keywords.append(word)
        keywords = ' '.join(keywords)
        return NewsKeywords(news=self.news, keywords=keywords)


class NewsKeywordsManager(LargeManager):
    def create_keywords(self):
        print dt(), '§ Create keywords '
        i = 0
        for news in self.iterate():
            i += 1
            if not i % 100:
                print dt(), '→ processed:', i
            news.create_keywords()


class NewsKeywords(models.Model):
    news = models.ForeignKey(News)
    keywords = models.TextField(blank=True)

    objects = NewsKeywordsManager()

    def create_keywords(self):
        words = self.keywords.split(' ')

        data = Counter(words).most_common()
        values = [item[1] for item in data]
        word_count = len(values)
        summa, average, deviation = average_deviation(values)

        NewsStats.objects.create(news=self, word_count=word_count, summa=summa,
                                 average=average, deviation=deviation)

        keywords = []
        alpha = 100
        beta = 100
        for word, count in Counter(words).most_common():
            weight = float(count) / summa
            if alpha_beta(count, average, deviation, alpha, beta):
                keyword = Keyword(news=self, word=word, count=count,
                                  weight=weight)
                keywords.append(keyword)
        Keyword.objects.bulk_create(keywords)


class NewsStats(models.Model):
    news = models.ForeignKey(News)
    word_count = models.IntegerField(default=0)
    summa = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    deviation = models.FloatField(default=0)


class Keyword(models.Model):
    news = models.ForeignKey(News)
    word = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0)
