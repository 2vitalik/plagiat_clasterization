import gc
from django.db import models
from sqlalchemy.types import LargeBinary
from libs.manager import LargeManager
from libs.tools import dt
from libs.xmath import vector_cos


class AbstractStats(models.Model):
    base = None
    word_count = models.IntegerField(default=0)
    summa = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    deviation = models.FloatField(default=0)

    class Meta:
        abstract = True


class NewsStats(AbstractStats):
    base = models.ForeignKey('main.News')

    class Meta:
        app_label = 'main'


class ParagraphStats(AbstractStats):
    base = models.ForeignKey('main.NewsParagraph')

    class Meta:
        app_label = 'main'


class CosResult(models.Model):
    news_1 = models.ForeignKey('main.News', related_name='cos1')
    news_2 = models.ForeignKey('main.News', related_name='cos2')
    doc_1 = models.IntegerField(default=0)
    doc_2 = models.IntegerField(default=0)
    cos = models.FloatField(default=-1, db_index=True)

    objects = LargeManager()

    class Meta:
        app_label = 'main'


class CosResultSeveral(models.Model):
    news_1 = models.ForeignKey('main.News', related_name='cos_1')
    news_2 = models.ForeignKey('main.News', related_name='cos_2')
    doc_1 = models.IntegerField(default=0)
    doc_2 = models.IntegerField(default=0)
    cos = models.FloatField(default=-1, db_index=True)

    class Meta:
        app_label = 'main'


class ParagraphCosResult(models.Model):
    paragraph_1 = models.ForeignKey('main.NewsParagraph', related_name='cos_1')
    paragraph_2 = models.ForeignKey('main.NewsParagraph', related_name='cos_2')
    cos = models.FloatField(default=-1, db_index=True)

    class Meta:
        app_label = 'main'


class AbstractKeywordItem(models.Model):
    base = None
    word = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0)

    class Meta:
        abstract = True


class NewsKeywordItemManager(LargeManager):
    def news_calculate_cosinuses(self, docs, news_docs, doc_ids=None):
        print dt(), 'calculate_cosinuses'
        data = dict()
        i = 0
        last1 = last2 = 0
        if doc_ids:
            doc_ids = set(doc_ids)
            news_ids = []
            for doc_id in doc_ids:
                news_ids.append(news_docs[doc_id])
            items = self.filter(base_id__in=news_ids)
            model = CosResultSeveral
        else:
            last = CosResult.objects.order_by('-pk')
            if last:
                last = last[0]
                last1 = last.news_1_id
                last2 = last.news_2_id
            items = self.iterate()
            model = CosResult
        print dt(), 'before big sql'
        for item in items:
            # news_id = item.news_id
            news_id = item.base.pk
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


class NewsKeywordItem(AbstractKeywordItem):
    base = models.ForeignKey('main.News')
    objects = NewsKeywordItemManager()

    class Meta:
        app_label = 'main'


class ParagraphKeywordItemManager(LargeManager):
    def paragraph_calculate_cosinuses(self, min_cos):
        print dt(), 'calculate_cosinuses'
        data = dict()
        i = 0
        last1 = last2 = 0
        last = CosResult.objects.order_by('-pk')
        if last:
            last = last[0]
            last1 = last.news_1_id
            last2 = last.news_2_id
        # items = CosResult.objects.iterate()
        items = CosResult.objects.filter(cos__gt=min_cos)
        print dt(), 'before filter by min_cos'
        pairs = list()
        news_ids = list()
        for item in items:
            # if item.cos < min_news_cos:
            #     continue
            pairs.append((item.news_1_id, item.news_2_id))
            news_ids.append(item.news_1_id)
            news_ids.append(item.news_2_id)
        news_ids = set(news_ids)
        for item in items:
            # news_id = item.news_id
            base_id = item.base.pk
            if not i % 1000:
                print dt(), 'loaded', i
            i += 1
            data.setdefault(base_id, dict())
            data[base_id][item.word] = item.weight
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
                results.append(ParagraphCosResult(
                    paragraph_1_id=news_id1,
                    paragraph_2_id=news_id2, cos=cos))
                j += 1
                if not j % 10000:
                    ParagraphCosResult.objects.bulk_create(results)
                    print dt(), 'added', j
                    results = []
            gc.collect()


class ParagraphKeywordItem(AbstractKeywordItem):
    base = models.ForeignKey('main.NewsParagraph')
    news = models.ForeignKey('main.News')
    objects = ParagraphKeywordItemManager()

    class Meta:
        app_label = 'main'
