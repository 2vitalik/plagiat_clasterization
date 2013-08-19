# coding: utf-8
from collections import Counter
from datetime import datetime
import os
import re
from subprocess import Popen, PIPE
from xml.etree import ElementTree
import sys
import math

from django.db import models

from libs.tools import w2u, chunks


class NewsManager(models.Manager):
    def load_from_folder(self, news_path):
        files = os.listdir(news_path)
        items = []
        for filename in files:
            if filename in ['.', '..']:
                continue
            news = self.load_from_xml("{}/{}".format(news_path, filename))
            items.append(news)
            # news.save()
        print '§ Total entries:', len(items)
        chunk_size = 250
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(self.bulk_create(chunk))
            print '→ Processed:', processed

    def load_from_xml(self, filename):
        print '→ Processing file:', filename
        text = open(filename).read()
        text = "<root>{}</root>".format(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<p>', '\n')
        text = text.replace('<>', ' ')
        text = w2u(text)
        tree = ElementTree.fromstring(text)
        data = {}
        for child in tree:
            name = child.tag
            value = child.text.strip()
            # print "[{}]=[{}]".format(child.tag, value.encode('utf-8'))
            data[name] = value
        doc_id = int(data['docID'][8:])
        return News(doc_id=doc_id, url=data['docURL'],
                    subject=data['subject'], agency=data['agency'],
                    date=data['date'], daytime=data['daytime'],
                    content=data['content'])

    def process_stems(self):
        i = 0
        for news in self.all():
            i += 1
            if not i % 200:
                print '→ processed:', i
            news.process_stem()

    def process_keywords(self):
        i = 0
        for news in self.all():
            i += 1
            if not i % 200:
                print '→ processed:', i
            news.process_keywords()

    def calc_keywords(self):
        i = 0
        dt = datetime.now().strftime("[%H:%M:%S]")
        print dt, 'calc_keywords'
        for news in self.only('doc_id', 'keywords'):
            if not i % 100:
                dt = datetime.now().strftime("[%H:%M:%S]")
                print dt, '→ processed:', i
            i += 1
            news.calc_keywords()
            # break


class News(models.Model):
    doc_id = models.IntegerField()
    url = models.URLField()
    subject = models.CharField(max_length=500)
    agency = models.CharField(max_length=100)
    date = models.IntegerField()
    daytime = models.IntegerField()
    content = models.TextField()
    stemmed = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

    objects = NewsManager()

    def stem(self):
        process = Popen('".data/mystem.exe" -cnig', shell=True, cwd='.',
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate(self.content.encode('cp1251'))
        return w2u(out)

    def old_process_stem(self):
        # sleep(0.3)
        print '\n' * 2
        print '→ Processing stem for', self.doc_id
        stem = self.stem()
        stemmed = []
        i = 1
        ok = True
        is_word = True
        lines = re.split('[\r\n]', stem)
        len1 = len(lines)
        lines = filter(str.strip, lines)  # удаление пустых строк
        len2 = len(lines)
        f = open('.data/stemmed/{}.txt'.format(self.doc_id), 'w')
        f.write('\n'.join(lines))
        f.close()
        # if len1 != len2:
        #     print >> sys.stderr, '× Были пустые строки!'
        for line in lines:
            if is_word:
                word = line.strip()
                if word == '-': continue
                word = re.sub('\(.*?\)', '', word)
                word = re.sub('=[^=]*?([|}])', '\\1', word)
                word = re.sub(',[^=]*?([|}])', '\\1', word)
                stemmed.append(word)
                if re.search(r'\\n|\\r|[_,(:);".0-9]', word) or not word:
                    if i == 1:
                        i += 1
                        continue
                    # print >> sys.stderr, '→ Processing stem for', self.doc_id
                    print >> sys.stderr, \
                        '× Error in line %d: "%s" is not word' % (i, word)
                    ok = False
                    # break
            else:
                delim = line.strip()
                if re.search(r'[А-Яа-я]', delim, re.UNICODE) or not delim:
                    # print >> sys.stderr, '→ Processing stem for', self.doc_id
                    print >> sys.stderr, \
                        '× Error in line %d: "%s" is not delim' % (i, delim)
                    ok = False
                    # break
            is_word = not is_word
            i += 1
        # if ok:
        #     self.stemmed = '\n'.join(stemmed)
        #     self.save()
            # print '· Успешно обработано %d строк.' % i
        # else:
        #     print >> sys.stderr, '× Ошибка обработки!'

    def process_stem(self):
        # print '\n'
        # print '→ Processing stem for', self.doc_id
        stem = self.stem()
        stemmed = []
        lines = re.split('[\r\n]', stem)
        lines = filter(str.strip, lines)  # удаление пустых строк
        # f = open('.data/stemmed/{}.txt'.format(self.doc_id), 'w')
        # f.write('\n'.join(lines))
        # f.close()
        for line in lines:
            word = line.strip()
            if re.search(r'\\n|\\r|[_":;]', word):
                # if re.search('[{}]', word):
                #     print word
                continue
            if len(word) < 5:
                continue
            if re.search('.*\{.*\}', word) and not re.match('(.*)\{(.*)\}', word):
                print word
            # if not re.search('.*\{.*\}', word):
            #     continue
            # word = re.sub('\(.*?\)', '', word)
            # word = re.sub('=[^=]*?([|}])', '\\1', word)
            # word = re.sub(',[^=]*?([|}])', '\\1', word)
            # stemmed.append(word)
        # self.stemmed = '\n'.join(stemmed)
        # self.save()

    def process_keywords(self):
        # print '→ Processing keywords for', self.doc_id
        lines = self.stemmed.split('\n')
        keywords = []
        for line in lines:
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
        self.keywords = ' '.join(keywords)
        # print self.keywords
        self.save()

    def calc_keywords(self):
        # print '→ Processing keywords for', self.doc_id
        words = self.keywords.split(' ')
        keywords = []
        word_count = 0
        summa = 0
        for word, count in Counter(words).most_common():
            word_count += 1
            summa += count
        if word_count <= 1:
            # print self.doc_id, '-', self.content
            return
        average = float(summa) / word_count
        deviation = 0
        for word, count in Counter(words).most_common():
            deviation += (count - average) ** 2
        deviation /= word_count - 1
        deviation = math.sqrt(deviation)
        # NewsStats(news=self, word_count=word_count, summa=summa,
        #           average=average, deviation=deviation).save()
        # print average, deviation

        alpha = 100
        beta = 100
        for word, count in Counter(words).most_common():
            weight = float(count) / summa
            if average - alpha * deviation <= count <= average + beta * deviation:
                keywords.append(Keyword(news=self, word=word, count=count, weight=weight))
        # Keyword.objects.bulk_create(keywords)


class NewsStats(models.Model):
    news = models.ForeignKey(News)
    word_count = models.IntegerField(default=0)
    summa = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    deviation = models.FloatField(default=0)


class Keyword(models.Model):
    news = models.ForeignKey(News)
    word = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0)
