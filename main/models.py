# coding: utf-8
import os
import re
import gc
from collections import Counter
from datetime import datetime
from django.db import models
from xml.etree import ElementTree
from libs.mystem import mystem
from libs.tools import w2u, chunks
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
        files = os.listdir(news_path)
        items = []
        for filename in files:
            news = self.load_from_xml("{}/{}".format(news_path, filename))
            items.append(news)
        print '§ Total entries:', len(items)
        chunk_size = 250
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(self.bulk_create(chunk))
            print '→ Processed:', processed

    def load_from_xml(self, filename):
        def fix_xml(text):
            text = "<root>{}</root>".format(text)
            text = text.replace('&', '&amp;')
            text = text.replace('<p>', '\n')
            text = text.replace('<>', ' ')
            return w2u(text)
        print '→ Processing file:', filename
        text = open(filename).read()
        tree = ElementTree.fromstring(fix_xml(text))
        data = {}
        for child in tree:
            name = child.tag
            value = child.text.strip()
            # print "[{}]=[{}]".format(child.tag, value.encode('utf-8'))
            data[name] = value
        doc_id = int(data['docID'][8:])
        return News(doc_id=doc_id, url=data['docURL'],
                    subject=data['subject'], agency=data['agency'],
                    date=data['date'], daytime=data['daytime'],
                    content=data['content'])

    def process_stems(self):
        i = 0
        for news in self.all():
            i += 1
            if not i % 200:
                print '→ processed:', i
            news.process_stem()

    def process_keywords(self):
        i = 0
        for news in self.all():
            i += 1
            if not i % 200:
                print '→ processed:', i
            news.process_keywords()

    def calc_keywords(self):
        i = 0
        dt = datetime.now().strftime("[%H:%M:%S]")
        print dt, 'calc_keywords'
        for news in self.only('doc_id', 'keywords'):
            if not i % 100:
                dt = datetime.now().strftime("[%H:%M:%S]")
                print dt, '→ processed:', i
            i += 1
            news.calc_keywords()
            # break


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


class NewsContent(models.Model):
    news = models.ForeignKey(News)
    content = models.TextField()

    def stem(self):
        return mystem(self.content)

    def create_stemmed(self):
        # print '→ Processing stem for', self.doc_id
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
                print word
            # if not re.search('.*\{.*\}', word):
            #     continue
            # word = re.sub('\(.*?\)', '', word)
            # word = re.sub('=[^=]*?([|}])', '\\1', word)
            # word = re.sub(',[^=]*?([|}])', '\\1', word)
            # stemmed.append(word)
        # self.stemmed = '\n'.join(stemmed)
        # self.save()


class NewsStemmed(models.Model):
    news = models.ForeignKey(News)
    stemmed = models.TextField(blank=True)

    def create_keywords(self):
        # print '→ Processing keywords for', self.doc_id
        lines = self.stemmed.split('\n')
        keywords = []
        for line in lines:
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
        self.keywords = ' '.join(keywords)
        # print self.keywords
        self.save()


class NewsKeywords(models.Model):
    news = models.ForeignKey(News)
    keywords = models.TextField(blank=True)

    def create_keywords(self):
        # print '→ Processing keywords for', self.doc_id
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
