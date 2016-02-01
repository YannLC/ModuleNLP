import unicodedata

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')


# Mots qui peuvent être transformé en faux amis par les regles 'suffixes'
defaultInvariants = 'I sure due done one issue max use six its she may they sex user normal here que Ile Paris Rennes basé à mis poste ete dès tél ENS base gene Latex EST CET unix linux'

# Mots dont le stem est irrégulier
defaultMap = {'ses': 'son',
              'nos': 'notre',
              'vos': 'votre',
              'eaux': 'eau',
              'ens': 'ENS',
              'la': 'le',


              'mais': 'but',
              'dans': 'in',
              'lorsque': 'when',
              'pays': 'country',
              'donné': 'data',
              'dos': 'back',
              'équipe': 'team',
              'mois': 'mounth',

            }

def lower(w):
    if len(w) > 1:
        yield w.lower()

def stripSuffixes(suffixes):
    def go(w):
        lenw = len(w)
        if lenw < 2 or w[-1] == w[-2]: # less, see, etc
            return
        for suf, repl in suffixes:
            suflen = len(suf)
            if w.endswith(suf) and len(w) >= suflen + 2:
                yield w[:-suflen] + repl
    return go


singularize = stripSuffixes([   ('ies', 'y'),
                                ('eaux', 'au'),
                                ('aux' , 'al'),
                                ('aux', 'ail'),
                                ('s' , ''),
                                ('x' , '')
                                ])

masculinize = stripSuffixes([   ('elle', 'eau'),
                                ('elle', 'el'),
                                ('nne', 'n'),
                                ('e' , ''),
                                ])

def stripHyphen(w):
    yield w.replace('-', '')

# French -> english
fr2enSuffixes = stripSuffixes([ ('el', 'al'),
                                ('ie', 'y'),
                                ('ique', 'ic'),
                                ])

def fr2en(w):
    if len(w) <= 3:
        return
    w = strip_accents(w)
    yield w
    yield from fr2enSuffixes(w)



class Stemmer:
    """ Stemmer basé sur un vocabulaire :
    Il établis une successions de cadidats et essaye de continuer la simplification pour chaque
    candidats appartenant au vocabulaire.
    Il ne peut inventer de mots, mais il existe toujours la possibilité de faux amis
    """
    def __init__(self, vocab, invariants=defaultInvariants, initmap=defaultMap):
        self.vocab = vocab
        self.termMap = initmap.copy()
        self.termMap.update({w:w for w in invariants.split()})
        self.ops = [lower, singularize, masculinize, stripHyphen, fr2en]


    def stem(self, w):
        termMap = self.termMap

        shortcut = termMap.get(w)
        if shortcut is not None:
            return shortcut

        vocab = self.vocab

        origs = set()
        origs.add(w)

        for op in self.ops:
            for candidate in op(w):
                if candidate != w and candidate in vocab:
                    origs.add(w)
                    w = candidate
                    break

            shortcut = termMap.get(w)
            if shortcut is not None:
                w = shortcut
                break


        for orig in origs:
            if orig in termMap:
                assert termMap[orig] != w
            else:
                termMap[orig] = w
        return w


    def printMapping(self):
        termMap = self.termMap
        reverse = dict()
        for k,v in termMap.items():
            #if not k.islower() and (k.lower() in termMap or k.lower() == v):
                #continue
            if k == v:
                continue
            reverse.setdefault(v, set()).add(k)

        reverse = list(reverse.items())
        if isinstance(self.vocab, dict):
            reverse.sort(key = lambda e: sum(self.vocab[k] for k in e[1] if k != e[0]) + self.vocab[e[0]])
            for v, ks in reverse:
                ks = ' '.join(k + '~' + str(self.vocab[k]) for k in ks if k.lower() != v)
                if ks:
                    v = v + '~' + str(self.vocab[v])
                    print(ks, '->', v)
        else:
            for v, ks in reverse:
                print(' '.join(ks), '->', v)

