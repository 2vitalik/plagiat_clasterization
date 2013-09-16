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
    bi_keys = set(dict1) & set(dict2)
    for key in bi_keys:
        mult += dict1[key] * dict2[key]
    for key in dict1:
        abs1 += dict1[key] ** 2
    for key in dict2:
        abs2 += dict2[key] ** 2
    return mult / (math.sqrt(abs1) * math.sqrt(abs2))
