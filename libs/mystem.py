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
    # print text
    # print repr(text)
    # out, err = process.communicate(text)
    # print len(out)
    # print '---'
    # print text.encode('utf-8')
    # print repr(text.encode('utf-8'))
    # out, err = process.communicate(text.encode('utf-8'))
    # print len(out)
    # print '---'
    # print text.encode('cp1251')
    # print repr(text.encode('cp1251'))
    out, err = process.communicate(text.encode('cp1251'))
    # print len(out)
    # print '---'
    # print text.encode('cp1251').decode('utf-8')
    # out, err = process.communicate(text.encode('cp1251'))
    # out, err = process.communicate(text.encode('utf-8'))
    # print out
    # print w2u(out)
    return w2u(out)
