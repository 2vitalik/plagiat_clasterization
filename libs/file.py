

def read_lines(filename):
    return open(filename).read().split('\n')


def file_save(filename, content, encode=None):
    f = open(filename, "w")
    if encode:
        content = content.encode(encode)
    f.write(content)
    f.close()
