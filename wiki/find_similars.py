# coding: utf-8
import os
from os.path import join
import re
from libs.file import save_file, load_file


def save_wiki_texts():
    import pywikibot
    site = pywikibot.getSite('ru', 'wikipedia')
    uk_site = pywikibot.getSite('uk', 'wikipedia')

    category = pywikibot.Category(site, u"Категория:Информатика")
    for article in category.articles():
        title = article.title()
        print title
        # content = article.get()
        # filename = join('data', title)
        # save_file(filename, content, 'utf-8')
        for link in article.langlinks():
            if link.site.code == 'uk':
                print " ", repr(link)
                print " ", link.site.code, link.title
                uk_page = pywikibot.Page(uk_site, link.title)
                try:
                    content = uk_page.get()
                    filename = join('data', "%s.uk" % title)
                    save_file(filename, content, 'utf-8')
                except pywikibot.exceptions.IsRedirectPage:
                    print "#" * 100
        # break


def load_wiki_texts():
    path = 'data/ru-uk'
    data = dict()
    for filename in os.listdir(path):
        filename = filename.decode('cp1251')
        title, lang = filename.split('.')
        data.setdefault(title, dict())
        data[title][lang] = load_file(join(path, filename))
    return data


def split_headers(text):
    return re.split('==[^=]+==', text)


def main(data):
    o = open('data/result.txt', 'w')
    for title, langs in data.items():
        # print title
        # for lang, content in langs.items():
        #     print lang
        texts2 = [langs['ru'], langs['uk']]
        texts2 = [re.sub('\{\{[^{}]+\}\}', '', text) for text in texts2]
        parts2 = [split_headers(text) for text in texts2]
        # for lang in parts2:
        #     for part in lang:
        #         print part.strip()
        #         print '-' * 200
        data = [list(), list()]  # two lists of blocks with sentences
        for i in [0, 1]:
            parts = parts2[i]
            for part in parts:
                sentences = re.split(r'\n\n|\.|(?<=\n)\*|(?<=\n) ', part)
                sentences = map(lambda s: s.strip(), sentences)
                sentences = map(lambda s: s.replace('\n', ' '), sentences)
                sentences = map(lambda s: s.replace('&nbsp;', ' '), sentences)
                sentences = map(lambda s: s.replace(' ', ' '), sentences)
                sentences = map(lambda s: re.sub('\[\[([^]]+)\|([^]]+)\]\]',
                                                 '\\2', s), sentences)
                sentences = map(lambda s: re.sub('\[\[([^]]+)\]\]',
                                                 '\\1', s), sentences)
                sentences = filter(len, sentences)
                data[i].append(sentences)
        # print '=' * 200
        # for sentences1 in data:
        #     for sentences in sentences1:
        #         print '-' * 100
        #         for sentence in sentences:
        #             # sentence = sentence.strip()
        #             # if sentence:
        #                 print u"→", sentence
        min_num_parts = min(len(data[0]), len(data[1]))
        for i in range(min_num_parts):
            min_num_sentences = min(len(data[0][i]), len(data[1][i]))
            for j in range(min_num_sentences):
                sentence0 = data[0][i][j]
                sentence1 = data[1][i][j]
                print '=' * 200
                print '-' * 200
                print sentence0
                print '-' * 200
                print sentence1
                print '-' * 200
                words0 = sentence0.split()
                words1 = sentence1.split()

                def remove_words(words):
                    new_words = []
                    for word in words:
                        # print repr(word)
                        # print repr('що')
                        if word not in ['який', 'яка', 'що', 'которий']:
                            new_words.append(word)
                    return new_words

                words0 = remove_words(words0)
                words1 = remove_words(words1)

                # for word in words0:
                #     print word
                # for word in words1:
                #     print word

                len0 = len(words0)
                len1 = len(words1)

                if len0 <= 1 or len1 <= 1:
                    print 'FAIL'
                    continue

                def check_words(words):
                    ok = False
                    for word in words:
                        if re.search('[А-Яа-я]', word):
                            ok = True
                    return ok

                if not check_words(words0) or not check_words(words1):
                    print 'FAIL'
                    continue

                min_num_words = min(len0, len1)
                print '1). Lengths:', len0, len1
                delta_len = abs(len1 - len0)
                ok1 = ok2 = ok3 = ok4 = False
                if delta_len <= 1 or delta_len / min_num_words <= 0.1:
                    print 'ok'
                    ok1 = True

                def count_cap(words):
                    count = 0
                    for word in words:
                        if re.search('[А-ЯA-Z]', word):
                            count += 1
                    return count

                def count_num(words):
                    count = 0
                    for word in words:
                        if re.match('\d+', word):
                            count += 1
                    return count

                def count_sum(words):
                    count = 0
                    for word in words:
                        if re.match('^\d+$', word):
                            count += int(word)
                    return count

                cap0 = count_cap(words0)
                cap1 = count_cap(words1)
                num0 = count_num(words0)
                num1 = count_num(words1)
                sum0 = count_sum(words0)
                sum1 = count_sum(words1)
                min_sum = min(sum0, sum1)

                print '2). Capitals:', cap0, cap1
                if abs(cap0 - cap1) <= 3:
                    print 'ok'
                    ok2 = True

                print '3). Numbers:', num0, num1
                if abs(num0 - num1) <= 2:
                    print 'ok'
                    ok3 = True

                print '4). Number values:', sum0, sum1
                if sum0 and sum1:
                    if abs(sum0 - sum1) / min_sum <= 0.15:
                        print 'ok'
                        ok4 = True
                else:
                    print 'ok'
                    ok4 = True

                if ok1 and ok2 and ok3 and ok4:
                    o.write(sentence0 + '\n' + sentence1 + '\n\n')

    o.close()

# save_wiki_texts()
data = load_wiki_texts()
main(data)
