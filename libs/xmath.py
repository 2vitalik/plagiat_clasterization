import math


def average_deviation(values):
    count = len(values)
    summa = 0
    for value in values:
        summa += value
    if count <= 1:
        # print self.doc_id, '-', self.content
        raise Exception('...')
    average = float(summa) / count
    deviation = 0
    for value in values:
        deviation += (value - average) ** 2
    deviation /= count - 1
    deviation = math.sqrt(deviation)
    return summa, average, deviation


def alpha_beta(value, average, deviation, alpha, beta):
    return average - alpha * deviation <= value <= average + beta * deviation
