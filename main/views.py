# coding: utf-8
from django.views.generic import TemplateView
from libs.logger import logger
from main.steps import Steps


class MainView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context.update({
            'steps': Steps.steps
        })
        return context

    def post(self, request, *args, **kwargs):
        logger.debug('¶')
        for step in request.POST:
            if step not in Steps.get_steps():
                continue
            getattr(Steps(), step)()
        return super(MainView, self).get(request, *args, **kwargs)
