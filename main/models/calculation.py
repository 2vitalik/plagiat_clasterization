from django.db import models


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
