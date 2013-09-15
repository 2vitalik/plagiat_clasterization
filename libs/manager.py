import gc
from django.db import models
from libs.timer import timer, td
from libs.tools import chunks, dt


class LargeManager(models.Manager):
    def iterate(self, chunksize=1000):
        pk = 0
        last_pk = self.order_by('-pk')[0].pk
        queryset = self.order_by('pk')
        while pk < last_pk:
            for row in queryset.filter(pk__gt=pk)[:chunksize]:
                pk = row.pk
                yield row
            gc.collect()

    @timer()
    def bulk(self, items, model, chunk_size):
        processed = 0
        for chunk in chunks(items, chunk_size):
            processed += len(model.objects.bulk_create(chunk))
            # print dt(), '-> Processed:', processed
            td('Processed: %d' % processed)
