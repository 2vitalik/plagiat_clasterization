# coding: utf-8
from collections import Counter
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from libs.manager import LargeManager
from libs.tools import dt
from libs.xmath import average_deviation, DeviationError, alpha_beta
from main.models.calculation import NewsKeywordItem, ParagraphKeywordItem
from main.models.calculation import NewsStats, ParagraphStats


class AbstractKeywordsManager(LargeManager):
    def __init__(self, stats_model):
        super(AbstractKeywordsManager, self).__init__()
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
            if stats:
                items.append(stats)
        print dt(), '@ Adding stats to DB'
        self.bulk(items, model=self.stats_model, chunk_size=1000)


class AbstractKeywords(models.Model):
    base = None
    keywords = models.TextField(blank=True)
    stats_model = None
    keyword_item_model = None

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
            print 'x Bad news (few words):', self.base
            return
        return self.stats_model(base=self.base, word_count=word_count,
                                summa=summa, average=average,
                                deviation=deviation)


class NewsKeywordsManager(AbstractKeywordsManager):
    def create_keyword_items(self, alpha, beta, several_news_ids=None,
                             gen_report=False):
        print dt(), '@ Create news keywords'
        i = 0
        report = None
        if gen_report:
            report_name = '.results/filter_ab_%.2f_%.2f.txt' % (alpha, beta)
            report = open(report_name, 'w')
        if several_news_ids:
            items = self.filter(base_id__in=several_news_ids)
        else:
            items = self.iterate()
        for news in items:
            i += 1
            if not i % 100:
                print dt(), '-> processed:', i
            news.create_keyword_items(alpha, beta, report)
        if gen_report:
            report.close()


class TitleKeywords(AbstractKeywords):
    base = models.ForeignKey('main.News')

    class Meta:
        app_label = 'main'


class NewsKeywords(AbstractKeywords):
    base = models.ForeignKey('main.News')
    objects = NewsKeywordsManager(NewsStats)
    stats_model = NewsStats
    keyword_item_model = NewsKeywordItem

    class Meta:
        app_label = 'main'

    def create_keyword_items(self, alpha, beta, report=None):
        words = self.keywords.split(' ')
        data = Counter(words).most_common()
        try:
            stats = self.stats_model.objects.get(base=self.base)
        except ObjectDoesNotExist:
            # print self.news_id
            return
        left = stats.average - alpha * stats.deviation
        right = stats.average + beta * stats.deviation
        if report:
            report.write("\n%s \n#%d: (avg=%.2f, s=%.2f): [%.2f, %.2f]\n" %
                         (self.base.subject.encode('cp1251'), self.base.doc_id,
                          stats.average, stats.deviation, left, right))
        keywords = []
        for word, count in data:
            weight = float(count) / stats.summa
            if alpha_beta(count, stats.average, stats.deviation, alpha, beta):
                if not report:
                    keyword = self.keyword_item_model(
                        base=self.base, word=word, count=count, weight=weight)
                    keywords.append(keyword)
            if report:
                if count < left:
                    report.write(" [<] %d - %s\n" % (count, word.encode('cp1251')))
                    # print self.news.doc_id, left, right, count, word
                elif count > right:
                    report.write(" [>] %d - %s\n" % (count, word.encode('cp1251')))
                    # print self.news.doc_id, left, right, count, word
                else:
                    report.write(" [=] %d - %s\n" % (count, word.encode('cp1251')))
        if not report:
            self.keyword_item_model.objects.bulk_create(keywords)


class ParagraphKeywordsManager(AbstractKeywordsManager):
    def create_keyword_items(self, all_paragraphs=None, news_by_paragraph=None,
                             valid_keywords=None):
        print dt(), '@ Create paragraph keywords'
        i = 0
        if all_paragraphs:
            items = self.filter(base_id__in=all_paragraphs)
        else:
            items = self.iterate()
        for news in items:
            i += 1
            if not i % 100:
                print dt(), '-> processed:', i
            news.create_keyword_items(news_by_paragraph, valid_keywords)


class ParagraphKeywords(AbstractKeywords):
    base = models.ForeignKey('main.NewsParagraph')
    objects = ParagraphKeywordsManager(ParagraphStats)
    stats_model = ParagraphStats
    keyword_item_model = ParagraphKeywordItem

    class Meta:
        app_label = 'main'

    def create_keyword_items(self, news_by_paragraph, valid_keywords):
        words = self.keywords.split(' ')
        data = Counter(words).most_common()
        try:
            stats = self.stats_model.objects.get(base=self.base)
        except ObjectDoesNotExist:
            return
        keywords = []
        news_id = news_by_paragraph[self.pk]
        for word, count in data:
            if word in valid_keywords[news_id]:
                weight = float(count) / stats.summa
                # kwargs = {}
                # if self.keyword_item_model == ParagraphKeywordItem:
                #     kwargs['news'] = self.base.news
                keyword = self.keyword_item_model(
                    base=self.base, word=word, count=count, weight=weight,
                    news=self.base.news)
                keywords.append(keyword)
        self.keyword_item_model.objects.bulk_create(keywords)
