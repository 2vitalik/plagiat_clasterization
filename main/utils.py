
def w2u(value):
    return value.decode('cp1251').encode('utf-8')


def chunks(items, chunk_len):
    """ Yield successive n-sized chunks from items """
    for i in xrange(0, len(items), chunk_len):
        yield items[i:i+chunk_len]
