# coding: utf-8
from libs.file import read_lines
from libs.timer import ts, tp, timer, td
from main.models import News, NewsContent, NewsParagraph, TitleStemmed, \
    NewsStemmed, ParagraphStemmed, NewsKeywords, ParagraphKeywords, \
    NewsKeywordItem, TitleKeywordItem, TitleKeywords, ParagraphKeywordItem
from plagiat_clasterization import settings


class MissedValueError(Exception):
    def __init__(self, var_name, method_name):
        message = u"Пустое поле \"{var_name}\", запустите шаг " \
                  u"\"{method_name}\"".format(var_name=var_name,
                                              method_name=method_name)
        message = message.encode('utf-8')
        # m = u"ы111{s}".format(s='1')
        # m = u"ы111%s" % '1'
        super(MissedValueError, self).__init__(message)


class Steps(object):
    steps = [
        {'slug': 'load_news_from_folder',
         'type': 'news',
         'title': "Загрузить новости из файлов",
         'in': 'xml-файлы',
         'out': 'News, NewsContent',
         'desc': ''},
        {'slug': 'create_paragraphs',
         'type': 'paragraphs',
         'title': "Разбить новости на абзацы",
         'in': 'News',
         'out': 'NewsParagraph',
         'desc': ''},
        {'slug': 'create_title_stemmed',
         'type': 'title',
         'title': 'Стемминг заголовков',
         'in': 'News',
         'out': 'NewsTitleStemmed',
         'desc': ''},
        {'slug': 'create_news_stemmed',
         'type': 'news',
         'title': 'Стемминг новостей',
         'in': 'NewsContent',
         'out': 'NewsStemmed',
         'desc': ''},
        {'slug': 'create_paragraph_stemmed',
         'type': 'paragraphs',
         'title': 'Стемминг абзацев',
         'in': 'NewsParagraph',
         'out': 'NewsParagraphStemmed',
         'desc': ''},
        {'slug': 'load_stop_words',
         'type': '',
         'title': 'Загрузить список стоп-слов',
         'desc': ''},
        {'slug': 'create_title_keywords',
         'type': 'title',
         'title': 'Ключевые слова в заголовках (морф + стоп)',
         'desc': ''},
        {'slug': 'create_news_keywords',
         'type': 'news',
         'title': 'Ключевые слова в новостях (морф + стоп)',
         'desc': ''},
        {'slug': 'create_paragraph_keywords',
         'type': 'paragraphs',
         'title': 'Ключевые слова в абзацах (морф + стоп)',
         'desc': ''},
        {'slug': 'create_news_stats',
         'type': 'news',
         'title': 'Статистика по новостям (сумма, отклон, ...)',
         'desc': ''},
        {'slug': 'create_paragraph_stats',
         'type': 'paragraphs',
         'title': 'Статистика по абзацам (сумма, отклон, ...)',
         'desc': ''},
        {'slug': 'build_docs_news_dependencies',
         'type': 'news',
         'title': '',
         'desc': ''},
        {'slug': 'load_several_clustered_news',
         'type': 'news',
         'title': '',
         'desc': ''},
        {'slug': 'load_paragraph_ids',
         'type': 'paragraphs',
         'title': '',
         'desc': ''},
        {'slug': 'load_news_keywords',
         'type': 'news',
         'title': '',
         'desc': ''},
        {'slug': 'load_title_keywords',
         'type': 'title',
         'title': '',
         'desc': ''},
        {'slug': 'gen_reports',
         'type': 'news',
         'title': 'Генерация отчетов по новостям (альфа-бета)',
         'desc': ''},
        {'slug': 'create_title_keyword_items',
         'type': 'title',
         'title': 'Ключевые слова в заголовках',
         'desc': ''},
        {'slug': 'create_news_keyword_items',
         'type': 'news',
         'title': 'Ключевые слова в новостях (альфа-бета, заголовки)',
         'desc': ''},
        {'slug': 'create_paragraph_keyword_items',
         'type': 'paragraphs',
         'title': 'Ключевые слова в абзацах (с учетом новостей)',
         'desc': ''},
        {'slug': 'calculate_news_cos',
         'type': 'news',
         'title': 'Косинусы углов между новостями',
         'desc': ''},
        {'slug': 'calculate_paragraph_cos',
         'type': 'paragraphs',
         'title': 'Косинусы углов между абзацами',
         'desc': ''},
    ]

    @staticmethod
    def get_steps():
        return [step['slug'] for step in Steps.steps]

    def load_news_from_folder(self):
        """ create News and NewsContent """
        News.objects.load_from_folder(settings.NEWS_PATH)

    def create_paragraphs(self):
        """ create NewsParagraph """
        NewsContent.objects.create_paragraphs()

    def create_title_stemmed(self):
        """ create TitleStemmed """
        News.objects.create_stems()

    def create_news_stemmed(self):
        """ create NewsStemmed """
        NewsContent.objects.create_stems()

    def create_paragraph_stemmed(self):
        """ create ParagraphStemmed """
        NewsParagraph.objects.create_stems()

    def load_stop_words(self):
        self.stop_words = read_lines('.conf/stop_words.txt', 'cp1251')

    def create_title_keywords(self):
        """ create TitleKeyword """
        TitleStemmed.objects.create_keywords(self.stop_words, angry_mode=True)

    def create_news_keywords(self):
        """ create NewsKeyword """
        NewsStemmed.objects.create_keywords(self.stop_words, angry_mode=True)

    def create_paragraph_keywords(self):
        """ create ParagraphKeyword """
        ParagraphStemmed.objects.create_keywords(self.stop_words,
                                                 angry_mode=True)

    def create_news_stats(self):
        """ create NewsStats """
        NewsKeywords.objects.create_stats()

    def create_paragraph_stats(self):
        """ create ParagraphStats """
        ParagraphKeywords.objects.create_stats()

    @timer()
    def build_docs_news_dependencies(self):
        self.docs_by_news = dict()
        self.news_by_docs = dict()
        for news in News.objects.only('doc_id'):
            self.docs_by_news[news.pk] = news.doc_id
            self.news_by_docs[news.doc_id] = news.pk

    @timer()
    def load_several_clustered_news(self):
        """ get 704 news """
        if not self.news_by_docs:
            raise MissedValueError('news_by_docs',
                                   'build_docs_news_dependencies')
        several_doc_ids = read_lines('.conf/clustered.txt')
        if not several_doc_ids:
            raise Exception(u'Ошибка загрузки файла clustered.txt')
        several_doc_ids = map(int, several_doc_ids)
        self.several_doc_ids = set(several_doc_ids)
        self.several_news_ids = list()
        for doc_id in several_doc_ids:
            self.several_news_ids.append(self.news_by_docs[doc_id])

    @timer()
    def load_paragraph_ids(self):
        items = NewsParagraph.objects.filter(news__in=self.several_news_ids)
        items = items.only('news')
        # paragraphs_by_news = dict()
        self.news_by_paragraph = dict()
        self.all_paragraphs = list()
        for item in items:
            # print item.pk, item.news.pk
            # paragraphs_by_news.setdefault(item.news.pk, list())
            # paragraphs_by_news[item.news.pk].append(item.pk)
            self.news_by_paragraph[item.pk] = item.news_id
            self.all_paragraphs.append(item.pk)

    @timer()
    def load_news_keywords(self):
        if not self.several_news_ids:
            raise MissedValueError('several_news_ids',
                                   'load_several_clustered_news')
        items = NewsKeywordItem.objects.filter(base__in=self.several_news_ids)
        items = items.only('word', 'base')
        ts('query')
        items = list(items)
        tp()
        self.valid_keywords = dict()
        for item in items:
            news_id = item.base_id
            self.valid_keywords.setdefault(news_id, list())
            self.valid_keywords[news_id].append(item.word)


    @timer()
    def load_title_keywords(self):
        if not self.several_news_ids:
            raise MissedValueError('several_news_ids',
                                   'load_several_clustered_news')
        items = TitleKeywordItem.objects.filter(base__in=self.several_news_ids)
        items = items.only('word', 'base')
        ts('query')
        items = list(items)
        tp()
        self.title_keywords = dict()
        for item in items:
            news_id = item.base_id
            self.title_keywords.setdefault(news_id, list())
            self.title_keywords[news_id].append(item.word)

    @timer()
    def gen_reports(self):
        coefficients = [(0, 100)]
        for alpha, beta in coefficients:
            td('alpha=%.2f, beta=%.2f' % (alpha, beta))
            NewsKeywords.objects.create_keyword_items(alpha, beta,
                                                      gen_report=True)

    def create_title_keyword_items(self):
        """ create TitleKeywordItem """
        TitleKeywords.objects.create_keyword_items()
        # TitleKeywords.objects.create_keyword_items(several_news_ids)

    def create_news_keyword_items(self):
        """ create NewsKeywordItem """
        alpha = 0
        beta = 100
        NewsKeywords.objects.create_keyword_items(alpha, beta,
                                                  self.several_news_ids,
                                                  self.title_keywords)

    def create_paragraph_keyword_items(self):
        """ create ParagraphKeywordItem """
        ParagraphKeywords.objects.create_keyword_items(self.all_paragraphs,
                                                       self.news_by_paragraph,
                                                       self.valid_keywords)

    def calculate_news_cos(self):
        """ calculate cosinuses for news """
        NewsKeywordItem.objects.news_calculate_cosinuses(self.docs_by_news,
                                                         self.news_by_docs,
                                                         self.several_doc_ids)
        # NewsKeywordItem.objects.news_calculate_cosinuses(self.docs_by_news,
        #                                                  self.news_by_docs)

    def calculate_paragraph_cos(self):
        """ calculate cosinuses for paragraphs """
        min_global_cos = 0.7
        ParagraphKeywordItem.objects. \
            paragraph_calculate_cosinuses(self.docs_by_news, min_global_cos)
        # ParagraphKeywordItem.objects.\
        #     paragraph_calculate_cosinuses(self.docs_by_news, min_global_cos,
        #                                   several=False)
