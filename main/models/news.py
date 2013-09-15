# coding: utf-8
import os
from xml.etree import ElementTree
from django.db import models
from libs.mystem import mystem
from libs.tools import dt, w2u
from main.models import AbstractCreateStemmedModel, TitleStemmed, \
    CreateStemmedManager
from main.models.news_content import NewsContent


class NewsManager(CreateStemmedManager):
    def load_from_folder(self, news_path):
        print dt(), '@ Loading files, adding news to DB, creating news_contests'
        files = os.listdir(news_path)
        items = []
        i = 0
        for filename in files:
            i += 1
            if not i % 500:
                print dt(), '-> processed:', i
            news_content = \
                self.load_from_xml("{}/{}".format(news_path, filename))
            items.append(news_content)
        print dt(), '-> Total entries:', len(items)
        print dt(), '@ Adding news_contests to DB'
        self.bulk(items, model=NewsContent, chunk_size=250)

    def load_from_xml(self, filename):
        def fix_xml(text):
            text = "<root>{}</root>".format(text)
            text = text.replace('&', '&amp;')
            text = text.replace('<p>', '\n')
            text = text.replace('<>', ' ')
            return w2u(text)
        # print '-> Processing file:', filename
        text = open(filename).read()
        tree = ElementTree.fromstring(fix_xml(text))
        data = {}
        for child in tree:
            name = child.tag
            value = child.text.strip()
            # print "[{}]=[{}]".format(child.tag, value.encode('utf-8'))
            data[name] = value
        doc_id = int(data['docID'][8:])
        news = News(doc_id=doc_id, url=data['docURL'],
                    subject=data['subject'], agency=data['agency'],
                    date=data['date'], daytime=data['daytime'])
        news.save()
        news_content = NewsContent(base=news, content=data['content'])
        return news_content


class News(AbstractCreateStemmedModel):
    doc_id = models.IntegerField()
    url = models.URLField()
    subject = models.CharField(max_length=500)
    agency = models.CharField(max_length=100)
    date = models.IntegerField()
    daytime = models.IntegerField()

    objects = NewsManager(TitleStemmed)
    stemmed_model = TitleStemmed

    class Meta:
        app_label = 'main'

    def __init__(self, *args, **kwargs):
        super(News, self).__init__(*args, **kwargs)
        self.base = self

    def stem(self):
        return mystem(self.subject)
