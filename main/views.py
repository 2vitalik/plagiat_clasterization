from django.views.generic import TemplateView
from main.steps import load_news_from_folder, create_paragraphs


class MainView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        steps = {
            load_news_from_folder: "create News and NewsContent",
            create_paragraphs: "create NewsParagraph",
        }
        context.update({
            'steps': steps
        })
        return context
