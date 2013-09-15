from main.models import News, NewsContent, NewsParagraph
from plagiat_clasterization import settings


class Steps(object):
    steps = {
        'load_news_from_folder': "create News and NewsContent",
        'create_paragraphs': "create NewsParagraph",
    }

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
