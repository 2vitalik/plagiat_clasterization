# coding: utf-8
import re
from django.db import models
from libs.mystem import mystem
from libs.tools import dt
from main.models.news import News
from main.models.paragraph import NewsParagraph
from main.models.stemmed import CreateStemmedManager, NewsStemmed


class NewsContentManager(CreateStemmedManager):
    def create_paragraphs(self):
        print dt(), '@ Creating paragraphs'
        i = 0
        items = []
        for news in self.iterate():
            i += 1
            # if i > 500:
            #     break
            if not i % 100:
                print dt(), '-> processed:', i
            paragraphs = news.create_paragraphs()
            items += paragraphs
        print dt(), '@ Adding paragraphs of DB'
        self.bulk(items, model=NewsParagraph, chunk_size=100)


class NewsContent(models.Model):
    news = models.ForeignKey(News)
    content = models.TextField()

    objects = NewsContentManager(NewsStemmed)

    class Meta:
        app_label = 'main'

    def stem(self):
        return mystem(self.content)

    def create_stemmed(self):
        # print dt(), self.news_id
        stem = self.stem()
        stemmed = []
        lines = re.split('[\r\n]', stem)
        lines = filter(str.strip, lines)  # удаление пустых строк
        for line in lines:
            word = line.strip()
            if re.search(r'\\n|\\r|[_":;]', word):
                # if re.search('[{}]', word):
                #     print word
                continue
            if len(word) < 5:
                continue
            if re.search('.*\{.*\}', word) and not re.match('(.*)\{(.*)\}', word):
                print '?', word
            if not re.search('.*\{.*\}', word):
                # print 'x', word
                continue
            word = re.sub('\(.*?\)', '', word)
            word = re.sub('=[^=]*?([|}])', '\\1', word)
            word = re.sub(',[^=]*?([|}])', '\\1', word)
            stemmed.append(word)
        return NewsStemmed(news=self.news, stemmed='\n'.join(stemmed))

    def create_paragraphs(self):
        paragraphs = self.content.split('\n')
        return [NewsParagraph(news=self.news, order=i, paragraph=paragraphs[i])
                for i in range(len(paragraphs))]
