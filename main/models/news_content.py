# coding: utf-8
from django.db import models
from libs.timer import timer, tc, ts, tp, td
from libs.tools import dt
from main.models.paragraph import NewsParagraph
from main.models.stemmed import CreateStemmedManager, NewsStemmed, \
    AbstractCreateStemmedModel


class NewsContentManager(CreateStemmedManager):
    @timer()
    def create_paragraphs(self):
        items = []
        ts('main loop')
        for news in self.iterate():
            tc(100)
            paragraphs = news.create_paragraphs()
            items += paragraphs
        tp()
        td('Adding paragraphs of DB')
        self.bulk(items, model=NewsParagraph, chunk_size=100)


class NewsContent(AbstractCreateStemmedModel):
    base = models.ForeignKey('main.News')
    objects = NewsContentManager(NewsStemmed)
    stemmed_model = NewsStemmed

    class Meta:
        app_label = 'main'

    def create_paragraphs(self):
        paragraphs = self.content.split('\n')
        return [NewsParagraph(news=self.base, order=i, content=paragraphs[i])
                for i in range(len(paragraphs))]
