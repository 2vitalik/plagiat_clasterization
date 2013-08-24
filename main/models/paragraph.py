from django.db import models
from main.models.news import News
from main.models.stemmed import CreateStemmedManager


class NewsParagraph(models.Model):
    news = models.ForeignKey(News)
    order = models.IntegerField(default=-1)
    paragraph = models.TextField()

    objects = CreateStemmedManager()

    class Meta:
        app_label = 'main'
