from django.db import models
from main.models.stemmed import CreateStemmedManager, AbstractCreateStemmedModel, ParagraphStemmed


class NewsParagraph(AbstractCreateStemmedModel):
    news = models.ForeignKey('main.News')
    order = models.IntegerField(default=-1)
    objects = CreateStemmedManager(ParagraphStemmed)
    stemmed_model = ParagraphStemmed

    class Meta:
        app_label = 'main'

    @property
    def base(self):
        return self
