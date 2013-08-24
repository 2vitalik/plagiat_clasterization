# coding: utf-8
from collections import Counter
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from libs.manager import LargeManager
from libs.tools import dt
from libs.xmath import average_deviation, DeviationError, alpha_beta
from main.models import NewsStats, Keyword
from main.models.news import News


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
        self.bulk(items, model=NewsStats, chunk_size=1000)

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

    class Meta:
        app_label = 'main'

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
                if not report:
                    keyword = Keyword(news=self.news, word=word, count=count,
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


class ParagraphKeywords(models.Model):
    news = models.ForeignKey(News)
    keywords = models.TextField(blank=True)
