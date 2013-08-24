# coding: utf-8
from django.db import models
from libs.tools import dt
from main.models.news import News
from main.models.paragraph import NewsParagraph
from main.models.stemmed import CreateStemmedManager, NewsStemmed, AbstractCreateStemmedModel


class NewsContentManager(CreateStemmedManager):
    def create_paragraphs(self):
        print dt(), '@ Creating paragraphs'
        i = 0
        items = []
        for news in self.iterate():
            i += 1
            if not i % 100:
                print dt(), '-> processed:', i
            paragraphs = news.create_paragraphs()
            items += paragraphs
        print dt(), '@ Adding paragraphs of DB'
        self.bulk(items, model=NewsParagraph, chunk_size=100)


class NewsContent(AbstractCreateStemmedModel):
    base = models.ForeignKey(News)
    objects = NewsContentManager(NewsStemmed)

    class Meta:
        app_label = 'main'

    def create_paragraphs(self):
        paragraphs = self.content.split('\n')
        return [NewsParagraph(news=self.base, order=i, paragraph=paragraphs[i])
                for i in range(len(paragraphs))]
