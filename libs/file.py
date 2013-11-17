import re


def read_lines(filename, decode=None):
    lines = re.split(r'[\n\r]+', open(filename).read())
    if decode:
        lines = map(lambda x: x.decode(decode), lines)
    return lines


def save_file(filename, content, encode=None):
    f = open(filename, "w")
    if encode:
        content = content.encode(encode)
    f.write(content)
    f.close()


def save_lines(filename, lines, encode=None):
    save_file(filename, '\n'.join(lines), encode)


def load_file(filename):
    return file(filename).read().replace('\r', '')
