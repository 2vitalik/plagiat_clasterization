from main.models import News, NewsContent, NewsParagraph
from plagiat_clasterization import settings


def load_news_from_folder():
    """ create News and NewsContent """
    News.objects.load_from_folder(settings.NEWS_PATH)


def create_paragraphs():
    """ create NewsParagraph """
    NewsContent.objects.create_paragraphs()


def create_title_stemmed():
    """ create TitleStemmed """
    News.objects.create_stems()


def create_news_stemmed():
    """ create NewsStemmed """
    NewsContent.objects.create_stems()


def create_paragraph_stemmed():
    """ create ParagraphStemmed """
    NewsParagraph.objects.create_stems()
