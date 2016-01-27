import time
import os
from collections import Counter
from nltk import tekenize
import re


sentences_tokenizer = tokenize.load('tokenizers/punkt/french.pickle')
#word_tokenizer = tokenize.TweetTokenizer(preserve_case=False, reduce_len=False, strip_handles=False)
#word_tokenizer = tokenize.TreebankWordTokenizer()
word_tokenizer = tokenize.RegexpTokenizer(pattern=r'[\w-]+|[^\w\s]+')



url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
mail_re = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
symbols = ['_symbol_', '_year_', '_hour_', '_number_', '_url_', '_email_']
allsymbols = set()

def cleanWords(words):
    for word in words:
        l = len(word)
        lword = word.lower()
        wordWoHyphen = word.replace('-', '')

        if wordWoHyphen.isalpha():
            yield word
        elif word.isdecimal():
            v = int(word)
            if 1000 < v < 2100:
                yield "_year_"
            else:
                yield "_number_"
        elif wordWoHyphen.isalnum():
            left, center, right = lword.partition('h')
            if left.isdecimal() and center == 'h' and right.isdecimal():
                yield "_hour_"
            else:
               Exception('Unknown alphanum word class :' + repr(word))
        elif word[0] == '_' and word[-1] == '_':
            yield word
        elif l <= 2 and all(c in '«»‘’\'"{[()]}.,;:…?&-/' for c in word):
            #print([c for c in word])
            for c in word:
                if c in "«»‘":
                    yield '"'
                if c == '’':
                    yield "'"
                elif c == '…':
                    yield '...'
                else:
                    yield c
        else:
            if word == '...':
                yield '...'
            else:
                allsymbols.add(word)
                yield '_symbol_'

def iterTokenizedSentences(txt, sectiontitle=None, tags=[], min_sent_length=3):
    for par in iterParagraphs(txt):
        # Nétoie les symboles
        par = url_re.sub('_url_', par)
        par = par.replace(' [dot] ', '.')
        par = par.replace(' [at] ', '@')
        par = mail_re.sub('_email_', par)

        # Pour chaque phrase du contenu :
        for sent in sentences_tokenizer.tokenize(par):
            sent = word_tokenizer.tokenize(sent)
            sent = list(cleanWords(sent))

            if len(sent) >= min_sent_length:
                yield sent


def iterParagraphs(txt):
    """
    Generateur produisant à partir d'une chaine des paragraphes§ sans \n, prets pour le tokenizer.

    Deux § sont séparés par une ligne vide. Un titre est aussi un paragraphe.
    """
    accum = []
    for line in txt.splitlines():
        line = line.strip()
        breakp = False
        if line:
            # Analyse le premier caractère de la ligne pour déterminer
            # s'il faut casser le paragraphe
            c0 = line[0]
            if c0.isalnum():
                # Une ligne en début de §, commençant par un chiffre
                # est sur son propre §.
                if not accum and c0.isnumeric():
                    yield line
                    continue
            elif c0 not in '[("\'':
                # Une ligne commençant par un caractère spécial
                # débute un §.
                breakp = True
                # Supprime les chr spéciaux.
                while line and not line[0].isalnum():
                    line = line[1:].strip()
        else:
            # Ligne vide -> nouveau §
            breakp = True

        if breakp and accum:
            # Vide l'accumulateur
            yield ' '.join(accum)
            accum = []

        if line:
            accum.append(line)

    if accum:
        yield ' '.join(accum)


def filterSentences(sents, min_count=10, min_WordsOverMC=3, min_pWordOverMC=0.75):
    sents = list(sents)

    c = Counter(w for s in sents for w in s if w not in symbols)

    acc = []
    for sent in sents:
        wordsOverMC = sum(c[w] > min_count for w in sent)
        min_wordsOverMC = max(min_pWordOverMC * len(sent), min_WordsOverMC)
        if wordsOverMC >= min_wordsOverMC:
            acc.append(sent)
    print('removed {} sentences over a total of {} sentences.'.format(len(sents)-len(acc),len(sents)))
    return acc

def trigrams(sents, min_coun=15, threshold=25):
    biTrans = gensim.models.Phrases(sents, min_count=min_coun, threshold=threshold)
    bi = biTrans[sents]
    triTrans = gensim.models.Phrases(bi, min_count=min_coun, threshold=threshold)
    tri = triTrans[bi]
    return tri
