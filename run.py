import os
import subprocess
import sys
from main.utils import w2u

path = os.path.dirname(__file__)  # 'd:/Dropbox/Development/univer/plagiat_clasterization/'
os.chdir(path)
sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plagiat_clasterization.settings")

from main.models import News

# # fill out database
# # News.objects.load_from_folder('.data/news')
#
# # print News.objects.get(doc_id=1495).stem()
#
# # process stems (first step)
# # News.objects.process_stems()
#
# # News.objects.get(doc_id=1).old_process_stem()
#
# # for doc_id in [12603, 1267, 15000, 2323, 24376, 24635, 24770, 2636, 27119, 2803, 28034, 2814, 28966, 3001, 33961, 33976, 3887, 3926, 4520, 45951, 45955, 4860, 5618, 5720, 59096, 59097, 62050, 63348, 63386, 6378, 68379, 76639, 77094, 77096, 9437]:
# # for doc_id in [1267, 2323, 24635, 24770, 2636, 27119, 2803, 2814, 28966, 3001, 33961, 33976, 3887, 3926, 4520, 45951, 45955, 5618, 5720, 59096, 59097, 62050, 63348, 63386, 6378, 68379, 76639, 77094, 77096, 9437]:
# #     News.objects.get(doc_id=doc_id).process_stem()

# News.objects.process_keywords()
News.objects.calc_keywords()
