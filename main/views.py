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
        steps = list()
        for step in request.POST:
            if step not in Steps.get_steps():
                continue
            steps.append(step)
        steps = sorted(steps, key=lambda step: Steps.step_index(step))
        app = Steps()
        for step in steps:
            print '#' * 80
            print '#' * 1, step
            print '#' * 80
            getattr(app, step)()
        return super(MainView, self).get(request, *args, **kwargs)
