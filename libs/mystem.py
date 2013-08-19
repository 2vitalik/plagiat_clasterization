from subprocess import Popen, PIPE
from libs.tools import w2u


def mystem(text):
    process = Popen('".data/mystem.exe" -cnig', shell=True, cwd='.',
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate(text.encode('cp1251'))
    return w2u(out)
