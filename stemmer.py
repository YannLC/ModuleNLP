
# Mots qui peuvent être transformé en faux amis par les regles 'suffixes'
defaultInvariants = 'due one max use six its she may they sex user normal here que Ile Paris Rennes poste ete mais mois tél aller ENS ens celle regarder lorsque pays dos poster Latex EST'

# Mots dont le stem est irrégulier
defaultMap = {'ses': 'son',
              'nos': 'notre',
              'vos': 'votre',
              'bonne': 'bon',
              'eaux': 'eau',
              'were': 'be',
              'was': 'be',
              'are': 'be',
              'seen': 'see',
              'shown': 'show',
              'hidden': 'hide',
              'went': 'go',
              'gone': 'go',
              'sent': 'sent',
              'had': 'have',
              'has': 'have',
              'said': 'say',
              'done': 'do',
              'an': 'a'
            }

suffixes = [
            ('ing', ''),
            ('ation', 'er'),
            ('ique', 'ic'),
            ('ical', 'y'),

            ('ies', 'y'),
            ('eaux', 'au'),
            ('aux' , 'al'),
            ('aux', 'ail'),
            ('s' , ''),
            ('x' , ''),

            ('elle', 'el'),
            ('e' , ''),

            ('é' , ''),
            ('é' , 'er'),
            ('er', ''),
            ('ed', ''),
           ]

class Stemmer:
    """ Stemmer basé sur un vocabulaire :
    Il établis une successions de cadidats et essaye de continuer la simplification pour chaque
    candidats appartenant au vocabulaire.
    Il ne peut inventer de mots, mais il existe toujours la possibilité de faux amis
    """
    def __init__(self, vocab, invariants=defaultInvariants, initmap=defaultMap, suffixes=suffixes):
        self.vocab = vocab
        self.suffixes = suffixes
        self.termMap = initmap.copy()
        self.termMap.update({w:w for w in invariants.split()})


    def stem(self, w):
        termMap = self.termMap

        if w in termMap:
            return termMap[w]

        lenw = len(w)


        if lenw <= 2 or w[-1] == w[-2]: # see, fee, less, is, as, etc
            if w != 'I':
                return w.lower()
            else:
                return w



        candidates = set()
        candidates.add(w.lower())

        for suf, repl in suffixes:
            suflen = len(suf)
            if w.endswith(suf) and lenw > suflen:
                cand = w[:-suflen] + repl
                candidates.add(cand)

        for candidate in candidates:
            if candidate == w:
                continue
            if candidate in self.vocab and len(candidate) > 1:
                res = self.stem(candidate)
                termMap[w] = res
                return res

        return w


    def printMapping(self):
        termMap = self.termMap
        for k,v in termMap.items():
            if not k.islower() and (k.lower() in termMap or k.lower() == v):
                continue
            if k == v:
                continue
            print(k,'->',v)
