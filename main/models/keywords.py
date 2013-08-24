# coding: utf-8
from collections import Counter
import gc
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from libs.manager import LargeManager
from libs.tools import dt
from libs.xmath import average_deviation, DeviationError, alpha_beta, vector_cos
from main.models.calculation import CosResultSeveral, CosResult, NewsStats, ParagraphStats


class NewsKeywordsManager(LargeManager):
    def __init__(self, stats_model):
        super(NewsKeywordsManager, self).__init__()
        self.stats_model = stats_model

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
        self.bulk(items, model=self.stats_model, chunk_size=1000)

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


class AbstractKeywords(models.Model):
    base = None
    keywords = models.TextField(blank=True)

    class Meta:
        abstract = True

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
        return NewsStats(news=self.base, word_count=word_count,
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
                if not report:
                    keyword = Keyword(news=self.base, word=word, count=count,
                                      weight=weight)
                    keywords.append(keyword)
            if report:
                if count < left:
                    report.write(" [<] %d - %s\n" % (count, word.encode('cp1251')))
                    # print self.news.doc_id, left, right, count, word
                if count > right:
                    report.write(" [>] %d - %s\n" % (count, word.encode('cp1251')))
                    # print self.news.doc_id, left, right, count, word
        if not report:
            Keyword.objects.bulk_create(keywords)


class NewsKeywords(AbstractKeywords):
    base = models.ForeignKey('main.News')
    objects = NewsKeywordsManager(NewsStats)

    class Meta:
        app_label = 'main'


class ParagraphKeywords(AbstractKeywords):
    base = models.ForeignKey('main.NewsParagraph')
    objects = NewsKeywordsManager(ParagraphStats)

    class Meta:
        app_label = 'main'


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
    news = models.ForeignKey('main.News')
    word = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0)

    objects = KeywordManager()

    class Meta:
        app_label = 'main'
