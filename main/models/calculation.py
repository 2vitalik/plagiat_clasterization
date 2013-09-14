import gc
from django.db import models
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
    news_1 = models.ForeignKey('main.News', related_name='paragraph_cos_1')
    news_2 = models.ForeignKey('main.News', related_name='paragraph_cos_2')
    paragraph_1 = models.ForeignKey('main.NewsParagraph', related_name='cos_1')
    paragraph_2 = models.ForeignKey('main.NewsParagraph', related_name='cos_2')
    cos = models.FloatField(default=-1, db_index=True)

    class Meta:
        app_label = 'main'


class ParagraphCosResultSeveral(models.Model):
    news_1 = models.ForeignKey('main.News', related_name='paragraph_cos_1s')
    news_2 = models.ForeignKey('main.News', related_name='paragraph_cos_2s')
    paragraph_1 = models.ForeignKey('main.NewsParagraph', related_name='cos_1s')
    paragraph_2 = models.ForeignKey('main.NewsParagraph', related_name='cos_2s')
    cos = models.FloatField(default=-1, db_index=True)

    class Meta:
        app_label = 'main'


class CosResultAfterParagraph(models.Model):
    news_1 = models.ForeignKey('main.News', related_name='good_cos_1')
    news_2 = models.ForeignKey('main.News', related_name='good_cos_2')
    cos = models.FloatField(default=-1, db_index=True)
    doc_1 = models.IntegerField(default=0)
    doc_2 = models.IntegerField(default=0)

    class Meta:
        app_label = 'main'


class CosResultAfterParagraphSeveral(models.Model):
    news_1 = models.ForeignKey('main.News', related_name='good_cos_1s')
    news_2 = models.ForeignKey('main.News', related_name='good_cos_2s')
    cos = models.FloatField(default=-1, db_index=True)
    doc_1 = models.IntegerField(default=0)
    doc_2 = models.IntegerField(default=0)

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
        model.objects.bulk_create(results)
        print dt(), 'added', j


class NewsKeywordItem(AbstractKeywordItem):
    base = models.ForeignKey('main.News')
    objects = NewsKeywordItemManager()

    class Meta:
        app_label = 'main'


class ParagraphKeywordItemManager(LargeManager):
    def paragraph_calculate_cosinuses(self, docs, min_global_cos,
                                      several=True, save_good_news=True):
        print dt(), 'calculate_cosinuses'
        data = dict()
        i = 0
        # last1 = last2 = 0
        # last = CosResult.objects.order_by('-pk')
        # if last:
        #     last = last[0]
        #     last1 = last.news_1_id
        #     last2 = last.news_2_id
        # items = CosResult.objects.iterate()
        if several:
            cos_results_model = CosResultSeveral
            paragraph_cos_results_model = ParagraphCosResultSeveral
            good_cos_results_model = CosResultAfterParagraphSeveral
        else:
            cos_results_model = CosResult
            paragraph_cos_results_model = ParagraphCosResult
            good_cos_results_model = CosResultAfterParagraph
        # todo: get all (!!!) pairs (except cos=0 and cos>0.95)
        # items = cos_results_model.objects.filter(cos__gt=min_cos)
        items = cos_results_model.objects.exclude(cos=0).exclude(cos=1)
        print dt(), '-> filter by min_cos (and getting news)'
        pairs = list()
        news_ids = list()
        for item in items:
            # if item.cos < min_news_cos:
            #     continue
            pairs.append((item.news_1_id, item.news_2_id, item.cos))
            news_ids.append(item.news_1_id)
            news_ids.append(item.news_2_id)
        news_ids = set(news_ids)
        print dt(), '-> filter paragraph keyword items by that news'
        items = ParagraphKeywordItem.objects.filter(news_id__in=news_ids)
        for item in items:
            news_id = item.news_id
            paragraph_id = item.base_id
            if not i % 10000:
                print dt(), '   loaded keywords:', i
            i += 1
            data.setdefault(news_id, dict())
            data[news_id].setdefault(paragraph_id, dict())
            data[news_id][paragraph_id][item.word] = item.weight
            # if news_id > 50:
            #     break
        print dt(), '   loaded keywords:', i
        results = []
        best_results = []
        i = j = p = c = 0
        pairs_ok = list()
        print dt(), '-> processing all pairs:', len(pairs)
        for news_id_1, news_id_2, news_cos in pairs:
            pair_ok = False
            i += 1
            max_local_cos = -1
            best_paragraph_1 = -1
            best_paragraph_2 = -1
            if not i % 10:
                print dt(), '   processed pairs: ', i
            for paragraph_id_1, paragraph_1 in data[news_id_1].items():
                # if news_id1 < last1:
                #     continue
                for paragraph_id_2, paragraph_2 in data[news_id_2].items():
                    if paragraph_id_2 <= paragraph_id_1:
                        continue
                    # if last1 == news_id1 and news_id2 <= last2:
                    #     continue
                    cos = vector_cos(paragraph_1, paragraph_2)
                    # results.append(paragraph_cos_results_model(
                    #     news_1_id=news_id_1, paragraph_1_id=paragraph_id_1,
                    #     news_2_id=news_id_2, paragraph_2_id=paragraph_id_2,
                    #     cos=cos))
                    if cos > min_global_cos:
                        pair_ok = True
                    if cos > max_local_cos:
                        max_local_cos = cos
                        best_paragraph_1 = paragraph_id_1
                        best_paragraph_2 = paragraph_id_2
                    # todo: calc and save max paragraph cos
                    # j += 1
                    # if not j % 10000:
                    #     paragraph_cos_results_model.objects.bulk_create(results)
                    #     print dt(), '   paragraph cos added:', j
                    #     results = []
                gc.collect()
            if max_local_cos != -1:
                c += 1
                best_results.append(paragraph_cos_results_model(
                    news_1_id=news_id_1, paragraph_1_id=best_paragraph_1,
                    news_2_id=news_id_2, paragraph_2_id=best_paragraph_2,
                    cos=max_local_cos))
                if not c % 100:
                    paragraph_cos_results_model.objects.bulk_create(best_results)
                    print dt(), '   best cos of paragraphs added:', c
                    best_results = []
            if save_good_news and pair_ok:
                p += 1
                pairs_ok.append(good_cos_results_model(
                    news_1_id=news_id_1, news_2_id=news_id_2,
                    doc_1=docs[news_id_1], doc_2=docs[news_id_2],
                    cos=news_cos))
                if not p % 100:
                    good_cos_results_model.objects.bulk_create(pairs_ok)
                    print dt(), '   good pairs of news added:', p
                    pairs_ok = []
        # paragraph_cos_results_model.objects.bulk_create(results)
        # print dt(), '-> paragraph cos added:', j
        paragraph_cos_results_model.objects.bulk_create(best_results)
        print dt(), '   best cos of paragraphs added:', c
        if save_good_news:
            good_cos_results_model.objects.bulk_create(pairs_ok)
            print dt(), '-> good pairs of news added:', p


class ParagraphKeywordItem(AbstractKeywordItem):
    base = models.ForeignKey('main.NewsParagraph')
    news = models.ForeignKey('main.News')
    objects = ParagraphKeywordItemManager()

    class Meta:
        app_label = 'main'
