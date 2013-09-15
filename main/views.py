from django.views.generic import TemplateView
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
        for step in request.POST:
            if step not in Steps.steps.keys():
                continue
            getattr(Steps(), step)()
        return super(MainView, self).get(request, *args, **kwargs)
