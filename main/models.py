# coding: utf-8
import os
import pprint
import re
import gc
import time
from collections import Counter
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from xml.etree import ElementTree
import math
from libs.mystem import mystem
from libs.tools import w2u, chunks, dt
from libs.xmath import average_deviation, alpha_beta, DeviationError


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
        print dt(), '@ Loading files, adding news to DB, creating news_contests'
        files = os.listdir(news_path)
        items = []
        i = 0
        for filename in files:
            i += 1
            if not i % 500:
                print dt(), '-> processed:', i
            news_content = \
                self.load_from_xml("{}/{}".format(news_path, filename))
            items.append(news_content)
        print dt(), '-> Total entries:', len(items)
        print dt(), '@ Adding news_contests to DB'
        chunk_size = 250
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(NewsContent.objects.bulk_create(chunk))
            print '-> Processed:', processed

    def load_from_xml(self, filename):
        def fix_xml(text):
            text = "<root>{}</root>".format(text)
            text = text.replace('&', '&amp;')
            text = text.replace('<p>', '\n')
            text = text.replace('<>', ' ')
            return w2u(text)
        # print '-> Processing file:', filename
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
        print dt(), '@ Creating stems of news'
        i = 0
        items = []
        for news in self.iterate():
            i += 1
            # if i > 500:
            #     break
            if not i % 100:
                print dt(), '-> processed:', i
            stemmed = news.create_stemmed()
            items.append(stemmed)
        print dt(), '@ Adding stems of DB'
        chunk_size = 50
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(NewsStemmed.objects.bulk_create(chunk))
            print dt(), '-> Processed:', processed


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
            word = re.sub('\(.*?\)', '', word)
            word = re.sub('=[^=]*?([|}])', '\\1', word)
            word = re.sub(',[^=]*?([|}])', '\\1', word)
            stemmed.append(word)
        return NewsStemmed(news=self.news, stemmed='\n'.join(stemmed))


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
        chunk_size = 250
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(NewsKeywords.objects.bulk_create(chunk))
            print dt(), '-> Processed:', processed


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


class NewsKeywordsManager(LargeManager):
    def create_stats(self):
        print dt(), '@ Create stats'
        i = 0
        items = []
        for news in self.iterate():
            i += 1
            if not i % 1000:
                print dt(), '-> processed:', i
            stats = news.create_stats()
            # news.create_keywords(alpha, beta)
            if stats:
                items.append(stats)
        print dt(), '@ Adding stats to DB'
        chunk_size = 1000
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(NewsStats.objects.bulk_create(chunk))
            print dt(), '-> Processed:', processed

    def create_keywords(self, alpha, beta, gen_report=False):
        print dt(), '@ Create keywords'
        i = 0
        report = None
        if gen_report:
            report_name = '.results/filter_ab_%.2f_%.2f.txt' % (alpha, beta)
            report = open(report_name, 'w')
        for news in self.iterate():
            i += 1
            if not i % 1000:
                print dt(), '-> processed:', i
            news.create_keywords(alpha, beta, report)
        if gen_report:
            report.close()

class NewsKeywords(models.Model):
    news = models.ForeignKey(News)
    keywords = models.TextField(blank=True)

    objects = NewsKeywordsManager()

    def create_stats(self):
        words = self.keywords.split(' ')
        data = Counter(words).most_common()
        values = [item[1] for item in data]
        word_count = len(values)
        try:
            summa, average, deviation = average_deviation(values)
        except DeviationError:
            print 'x Bad news (few words):', self.news_id
            return
        return NewsStats(news=self.news, word_count=word_count,
                         summa=summa, average=average, deviation=deviation)

    def create_keywords(self, alpha, beta, report=None):
        words = self.keywords.split(' ')
        data = Counter(words).most_common()
        try:
            stats = NewsStats.objects.get(news=self.news)
        except ObjectDoesNotExist:
            # print self.news_id
            return
        left = stats.average - alpha * stats.deviation
        right = stats.average + beta * stats.deviation
        if report:
            report.write("\n#%d: (avg=%.2f, s=%.2f): [%.2f, %.2f]\n" %
                         (self.news.doc_id, stats.average, stats.deviation,
                          left, right))
        keywords = []
        for word, count in data:
            weight = float(count) / stats.summa
            if alpha_beta(count, stats.average, stats.deviation, alpha, beta):
                # keyword = Keyword(news=self.news, word=word, count=count,
                #                   weight=weight)
                # keywords.append(keyword)
                pass
            if report:
                if count < left:
                    report.write(" [<] %d - %s\n" % (count, word.encode('cp1251')))
                    # print self.news.doc_id, left, right, count, word
                if count > right:
                    report.write(" [>] %d - %s\n" % (count, word.encode('cp1251')))
                    # print self.news.doc_id, left, right, count, word
        # Keyword.objects.bulk_create(keywords)


class NewsStats(models.Model):
    news = models.ForeignKey(News)
    word_count = models.IntegerField(default=0)
    summa = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    deviation = models.FloatField(default=0)


class KeywordManager(LargeManager):
    def calculate_cosinuses(self, doc_ids=None):
        print dt(), 'calculate_cosinuses'
        docs = dict()
        news_docs = dict()
        for news in News.objects.only('doc_id'):
            docs[news.pk] = news.doc_id
            news_docs[news.doc_id] = news.pk
        data = dict()
        i = 0
        doc_ids = set(doc_ids)
        news_ids = []
        for doc_id in doc_ids:
            news_ids.append(news_docs[doc_id])
        print dt(), 'before big sql'
        # for item in self.iterate():
        for item in self.filter(news_id__in=news_ids):
            news_id = item.news_id
            # print news_id
            # print docs[news_id]
            if not i % 10000:
                print dt(), 'loaded', i
            i += 1
            # if docs[news_id] not in news_ids:
            #     continue
            data.setdefault(news_id, dict())
            # data[news_id].append(dict(word=item.word, weight=item.weight))
            data[news_id][item.word] = item.weight
            # if news_id > 50:
            #     break
        results = []
        i = 0
        j = 0
        for news_id1, news1 in data.items():
            i += 1
            doc1 = docs[news_id1]
            if not i % 10:
                print dt(), 'news', i
            # print dt(), news_id1
            for news_id2, news2 in data.items():
                if news_id2 <= news_id1:
                    continue
                doc2 = docs[news_id2]
                keys1 = dict(news1)
                keys2 = dict(news2)
                for key2 in keys2.keys():
                    if key2 not in keys1:
                        keys1[key2] = 0
                for key1 in keys1.keys():
                    if key1 not in keys2:
                        keys2[key1] = 0
                # print '=' * 100
                # for word, weight in keys1.items():
                #     print "%.3f, %s" % (weight, word)
                # print '=' * 100
                # for word, weight in keys2.items():
                #     print "%.3f, %s" % (weight, word)
                # print
                # if j > 0:
                #     break
                # print len(keys1), len(keys2)
                abs1 = 0
                abs2 = 0
                mult = 0
                for key in keys1.keys():
                    val1 = keys1[key]
                    val2 = keys2[key]
                    abs1 += val1 ** 2
                    abs2 += val2 ** 2
                    mult += val1 * val2
                cos = mult / (math.sqrt(abs1) * math.sqrt(abs2))
                results.append(CosResultSeveral(news_1_id=news_id1, doc_1=doc1,
                                         news_2_id=news_id2, doc_2=doc2,
                                         cos=cos))
                # results.append(CosResult(news_1_id=news_id2,
                #                          news_2_id=news_id1, cos=cos))
                j += 1
                if not j % 10000:
                    CosResultSeveral.objects.bulk_create(results)
                    print dt(), 'added', j
                    results = []
                # print news_id2, cos
        # chunk_size = 10000
        # processed = 0
        # for chunk in chunks(results, chunk_size):
        #     processed += len(CosResult.objects.bulk_create(chunk))
        #     print dt(), '-> Processed:', processed


class Keyword(models.Model):
    news = models.ForeignKey(News)
    word = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0)

    objects = KeywordManager()


class CosResult(models.Model):
    news_1 = models.ForeignKey(News, related_name='cos1')
    news_2 = models.ForeignKey(News, related_name='cos2')
    doc_1 = models.IntegerField(default=0)
    doc_2 = models.IntegerField(default=0)
    cos = models.FloatField(default=-1)


class CosResultSeveral(models.Model):
    news_1 = models.ForeignKey(News, related_name='cos_1')
    news_2 = models.ForeignKey(News, related_name='cos_2')
    doc_1 = models.IntegerField(default=0)
    doc_2 = models.IntegerField(default=0)
    cos = models.FloatField(default=-1)
