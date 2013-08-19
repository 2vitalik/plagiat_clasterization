

def read_lines(filename):
    return open(filename).read().split('\n')


def save_file(filename, content, encode=None):
    f = open(filename, "w")
    if encode:
        content = content.encode(encode)
    f.write(content)
    f.close()


def save_lines(filename, lines, encode=None):
    save_file(filename, '\n'.join(lines), encode)
