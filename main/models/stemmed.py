# coding: utf-8
import re
from django.db import models
from libs.manager import LargeManager
from libs.mystem import mystem
from libs.tools import dt
from main.models.keywords import NewsKeywords, ParagraphKeywords


class CreateStemmedManager(LargeManager):
    def __init__(self, stemmed_model):
        super(CreateStemmedManager, self).__init__()
        self.stemmed_model = stemmed_model

    def create_stems(self):
        print dt(), '@ Creating stems of news'
        i = 0
        items = []
        for news in self.iterate():
            i += 1
            if not i % 100:
                print dt(), '-> processed:', i
            stemmed = news.create_stemmed()
            items.append(stemmed)
        print dt(), '@ Adding stems of DB'
        self.bulk(items, model=self.stemmed_model, chunk_size=50)


class AbstractCreateStemmedModel(models.Model):
    base = None
    content = models.TextField()
    stemmed_model = None

    class Meta:
        abstract = True

    def stem(self):
        return mystem(self.content)

    def create_stemmed(self):
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
        return self.stemmed_model(base=self.base, stemmed='\n'.join(stemmed))


class CreateKeywordsManager(LargeManager):
    def __init__(self, keywords_model):
        super(CreateKeywordsManager, self).__init__()
        self.keywords_model = keywords_model

    def create_keywords(self):
        print dt(), '@ Extract list of valid keywords from stemmed data'
        i = 0
        items = []
        for news in self.iterate(100):
            i += 1
            if not i % 500:
                print dt(), '-> processed:', i
            news_keyword = news.create_keywords()
            items.append(news_keyword)
        print dt(), '@ Adding news_keywords to DB'
        self.bulk(items, model=self.keywords_model, chunk_size=250)

    class Meta:
        abstract = True


class AbstractStemmedModel(models.Model):
    base = None
    stemmed = models.TextField(blank=True)
    keywords_model = None

    class Meta:
        abstract = True

    def create_keywords(self):
        lines = self.stemmed.split('\n')
        keywords = []
        for line in lines:
            if not line:
                continue
            m = re.match('(.*)\{(.*)\}', line)
            stem = m.group(2)
            items = stem.split('|')
            forms = []
            for item in items:
                try:
                    word, word_type = item.split('=')
                except ValueError:
                    word, word_type = item, '?'
                if word_type in ['S', 'V', 'A', 'ADV']:
                    forms.append(word)
                    break  # use only first form
            for word in set(forms):
                keywords.append(word)
        keywords = ' '.join(keywords)
        return self.keywords_model(base=self.base, keywords=keywords)


class NewsStemmed(AbstractStemmedModel):
    base = models.ForeignKey('main.News')
    objects = CreateKeywordsManager(NewsKeywords)
    keywords_model = NewsKeywords

    class Meta:
        app_label = 'main'


class ParagraphStemmed(AbstractStemmedModel):
    base = models.ForeignKey('main.NewsParagraph')
    objects = CreateKeywordsManager(ParagraphKeywords)
    keywords_model = ParagraphKeywords

    class Meta:
        app_label = 'main'
