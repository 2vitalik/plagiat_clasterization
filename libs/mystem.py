import os
from subprocess import Popen, PIPE
from libs.tools import w2u


def mystem(text):
    if os.path.exists('/home/'):  # is linux?
        process = Popen('.mystem/mystem -cnig', shell=True, cwd='.',
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    else:  # else: windows
        process = Popen('".mystem/mystem.exe" -cnig', shell=False, cwd='.',
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate(text.encode('cp1251'))
    return w2u(out)
