# coding: utf-8
import re
import sys
from libs.file import save_lines


def old_process_stem(self):
    # sleep(0.3)
    print '\n' * 2
    print '→ Processing stem for', self.doc_id
    stem = self.stem()
    stemmed = []
    i = 1
    ok = True
    is_word = True
    lines = re.split('[\r\n]', stem)
    len1 = len(lines)
    lines = filter(str.strip, lines)  # удаление пустых строк
    len2 = len(lines)
    filename = '.data/stemmed/{}.txt'.format(self.doc_id)
    save_lines(filename, lines)
    # if len1 != len2:
    #     print >> sys.stderr, '× Были пустые строки!'
    for line in lines:
        if is_word:
            word = line.strip()
            if word == '-': continue
            word = re.sub('\(.*?\)', '', word)
            word = re.sub('=[^=]*?([|}])', '\\1', word)
            word = re.sub(',[^=]*?([|}])', '\\1', word)
            stemmed.append(word)
            if re.search(r'\\n|\\r|[_,(:);".0-9]', word) or not word:
                if i == 1:
                    i += 1
                    continue
                # print >> sys.stderr, '→ Processing stem for', self.doc_id
                print >> sys.stderr, \
                    '× Error in line %d: "%s" is not word' % (i, word)
                ok = False
                # break
        else:
            delim = line.strip()
            if re.search(r'[А-Яа-я]', delim, re.UNICODE) or not delim:
                # print >> sys.stderr, '→ Processing stem for', self.doc_id
                print >> sys.stderr, \
                    '× Error in line %d: "%s" is not delim' % (i, delim)
                ok = False
                # break
        is_word = not is_word
        i += 1
    # if ok:
    #     self.stemmed = '\n'.join(stemmed)
    #     self.save()
        # print '· Успешно обработано %d строк.' % i
    # else:
    #     print >> sys.stderr, '× Ошибка обработки!'
