import math


class DeviationError(Exception):
    pass

def average_deviation(values):
    count = len(values)
    summa = 0
    for value in values:
        summa += value
    if count <= 1:
        # print self.doc_id, '-', self.content
        raise DeviationError()
    average = float(summa) / count
    deviation = 0
    for value in values:
        deviation += (value - average) ** 2
    deviation /= count - 1
    deviation = math.sqrt(deviation)
    return summa, average, deviation


def alpha_beta(value, average, deviation, alpha, beta):
    return average - alpha * deviation <= value <= average + beta * deviation


def vector_cos(dict1, dict2):
    abs1 = abs2 = mult = 0
    all_keys = dict1.keys() + dict2.keys()
    for key in all_keys:
        val1 = dict1.get(key, 0)
        val2 = dict2.get(key, 0)
        abs1 += val1 ** 2
        abs2 += val2 ** 2
        mult += val1 * val2
    return mult / (math.sqrt(abs1) * math.sqrt(abs2))
