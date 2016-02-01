
# coding: utf-8

# In[4]:

from datetime import date
from emailparser import mailLoaderGen
from tokenizer import iterTokenizedSentences
from stemmer import Stemmer
from collections import Counter

fields = [
 'mailfile',
 'sujet',
 'from',
 'date',
 'tags',
 'sfbi_url',   
 'contact-nom',
 'contact-email',
 'date-candidature',
 'validite',
 'duree',
 'ville',
 'lieu',
 'labo',
 ]

outdir = 'archives_SFBI_AnnotationManuelle'

mails = list(mailLoaderGen())
words = Counter()
for mail in mails:
    mail.sents = list(iterTokenizedSentences(mail.description))
    for sent in mail.sents:
        words.update(sent)

stemmer = Stemmer(set(word for (word,n) in words.items() if n > 10))

for m in mails:
    outf = outdir + m.mailfile.strip('archives_SFBI')
    d = m.__dict__
    d['date'] = date.fromtimestamp(d['timestamp']).strftime("%d %B %Y")
    
    
    with open(outf, 'wt') as f:
        d['from'] = d.pop('sender')
        if m.sfbi:            
            ce = d['contact-email']
            ce = '\t'.join(ce) if type(ce) is set else ce
            d['contact-email'] = ce.replace(' [dot] ', '.').replace('[at]', '@')
            
            cn = d['contact-nom']
            d['contact-nom'] = '\t'.join(cn) if type(cn) is set else cn
                        
            if 'lieu' in d:
                #TODO: A mettre dans le parser web:
                d['lieu'] = d['lieu'].replace('\n\n', '\n')
            
            f.write("!!! Ceci est le contenu d'une annonce sur le site sfbi.fr.\n")
        for field in fields:
            if field in d:
                f.write('* {}: {}\n'.format(field, d[field]))
                

        f.write('-'*60 + '\n')

        f.write(m.description)

        f.write('-'*60 + '\n')

        for sent in m.sents:
            f.write(' '.join(stemmer.stem(word) for word in sent) + '\n')
