# coding: utf-8
import gc
from django.db import models
from libs.manager import LargeManager
from libs.tools import dt
from libs.xmath import vector_cos
from main.models.news import News


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
        if doc_ids:
            doc_ids = set(doc_ids)
            news_ids = []
            for doc_id in doc_ids:
                news_ids.append(news_docs[doc_id])
            items = self.filter(news_id__in=news_ids)
            last1 = last2 = 0
            model = CosResultSeveral
        else:
            last = CosResult.objects.order_by('-pk')[0]
            last1 = last.news_1_id
            last2 = last.news_2_id
            items = self.iterate()
            model = CosResult
        print dt(), 'before big sql'
        for item in items:
            news_id = item.news_id
            if not i % 10000:
                print dt(), 'loaded', i
            i += 1
            data.setdefault(news_id, dict())
            data[news_id][item.word] = item.weight
            # if news_id > 50:
            #     break
        results = []
        i = 0
        j = 0
        for news_id1, news1 in data.items():
            i += 1
            if not i % 10:
                print dt(), 'news', i
            if news_id1 < last1:
                continue
            for news_id2, news2 in data.items():
                if news_id2 <= news_id1:
                    continue
                if last1 == news_id1 and news_id2 <= last2:
                    continue
                cos = vector_cos(news1, news2)
                results.append(model(news_1_id=news_id1, doc_1=docs[news_id1],
                                     news_2_id=news_id2, doc_2=docs[news_id2],
                                     cos=cos))
                j += 1
                if not j % 10000:
                    model.objects.bulk_create(results)
                    print dt(), 'added', j
                    results = []
            gc.collect()


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
    cos = models.FloatField(default=-1, db_index=True)


class CosResultSeveral(models.Model):
    news_1 = models.ForeignKey(News, related_name='cos_1')
    news_2 = models.ForeignKey(News, related_name='cos_2')
    doc_1 = models.IntegerField(default=0)
    doc_2 = models.IntegerField(default=0)
    cos = models.FloatField(default=-1, db_index=True)


class ParagraphStats(models.Model):
    news = models.ForeignKey(News)
    word_count = models.IntegerField(default=0)
    summa = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    deviation = models.FloatField(default=0)

