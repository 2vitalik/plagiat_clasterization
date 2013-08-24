from django.db import models
from main.models.news import News
from main.models.stemmed import CreateStemmedManager, AbstractCreateStemmedModel, ParagraphStemmed


class NewsParagraph(AbstractCreateStemmedModel):
    news = models.ForeignKey(News)
    order = models.IntegerField(default=-1)
    objects = CreateStemmedManager(ParagraphStemmed)

    class Meta:
        app_label = 'main'

    @property
    def base(self):
        return self
