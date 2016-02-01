from logging import warning
from os import listdir, path

import email
import email.policy
import time

from urllib import request
try:
    import lxml.html
except ImportError:
    warning("No lxml module: can't parse html")

__all__ = ["Email", "mailLoaderGen"]

# Constantes
robotintro = "Une nouvelle offre d'emploi vient d'être postée sur le site www.sfbi.fr"
policy = email.policy.EmailPolicy(raise_on_defect=True, utf8=True)
parser = email.parser.BytesParser(policy=policy)


#
# Outils pour aider la lecture de mails
#

def decodeHeader(s):
    if "=?" in s:
        return ''.join(strbytes.decode('latin-1' if encoding is None else encoding)
                        for strbytes, encoding
                        in email.header.decode_header(s))
    else:
        return s

def extractTagsFromSubject(subject):
    tags = set()
    if subject is not None:
        for s in subject.split('['):
            i = s.find(']')
            if i != -1:
                tags.add(s[:i].strip())

    i = subject.rindex(']')
    if i != -1:
        subject = subject[i+1:]
    return tags, subject.strip()


#
# Outils pour aider la lecture de pages sfbi.fr d'annonce d'emplois
#

cachedir='cacheSFBI'
fieldtypeClass = 'field-type-'
fieldnameClass = 'field-field-emploi-'

def extractText(e, inP=False):
    text = e.text
    tail = e.tail
    tag = e.tag

    islabel = tag == "div" and "field-label" in e.attrib.get("class", "")

    acc = []

    if not islabel:
        if text:
            acc.append(text if inP else text.strip())

        # recursion
        acc.extend(extractText(c, inP=inP or tag == 'p') for c in e)

        if tag == 'br':
            acc.append('\n')
        elif tag == 'p' or tag == 'li':
            acc.append('\n\n')

    if tail:
        acc.append(tail if inP else tail.strip())

    return ''.join(acc)



class Email:

    def __init__(self, mailfile):
        self.mailfile = mailfile
        self.valid = True

    def load(self):
        with open(self.mailfile, 'rb') as fd:
            msg = parser.parse(fd)

        self.sender = decodeHeader(msg.get('From'))
        self.timestamp = time.mktime(email.utils.parsedate(msg.get('Date')))

        content = msg.get_content().lstrip()
        if content.startswith(robotintro):
            for line in content.splitlines():
                if line.startswith('http://'):
                    self._loadWebPage(line)
            self.sfbi = True
        else:
            self.sfbi = False
            self.tags, self.sujet = extractTagsFromSubject(decodeHeader(msg.get('Subject')))
            self.tags.remove('bioinfo')
            self.description = content

        return self

    def _loadWebPage(self, url, cachedir=cachedir):
        urlparts = url.split('/')
        cachefile = path.join(cachedir,'_'.join(urlparts[urlparts.index('')+1:]))

        if path.exists(cachefile):
            with open(cachefile, 'tr') as fd:
                html = fd.read()
        else:
            try:
                print("Downloading", url)
                html = request.urlopen(request.quote(url, safe=':/%')).read().decode('utf-8')
            except request.HTTPError as e:
                html = str(e.getcode())
            with open(cachefile, 'tw') as fd:
                fd.write(html)

        # Il y a quelques 404, ils sont mis en cache et repérés par une str
        if html == '404' or html == '403':
            warning('Error {}: {}.'.format(html, url))
            self.valid = False
            return

        #html = lxml.html.clean.clean_html(html)

        sectiondiv = lxml.html.fromstring(html).xpath('//div[@class="section"]')[0]
        self.sujet = sectiondiv.xpath('//h1[@class="title"]/text()')[0]
        self.sfbi_url = url

        for entry in sectiondiv.xpath('//div[contains(@class,"node-type-emploi")]/div[@class="content"]/div'):
            classes = entry.attrib['class'].split(' ')
            assert 'field' in classes

            # La classe du div renseigne sur le nom et le type de champs
            fieldname = None
            fieldtype = None
            for c in classes:
                if c.startswith(fieldtypeClass):
                    fieldtype = c[len(fieldtypeClass):]
                if c.startswith(fieldnameClass):
                    fieldname = c[len(fieldnameClass):]
            assert fieldname is not None and fieldtype is not None

            items = entry.xpath('div[@class="field-items"]/div[contains(@class, "field-item ")]')

            assert len(items) > 0
            if len(items) > 1:
                content = set(extractText(i).strip() for i in items)
            else:
                content = extractText(items[0]).replace('\xa0', ' ').strip()

            setattr(self, fieldname, content)


archivedir = 'archives_SFBI/2015_06_10-bioinfo_archives_annee_2014'
def mailLoaderGen(archivedir=archivedir):
    dedup = {}
    for mounth in listdir(archivedir):
        mounthdir = path.join(archivedir, mounth)
        for mailfn in listdir(mounthdir):
            # Passe sur les fichiers .recoded
            if mailfn.endswith(".recoded"):
                continue
            mailfile = path.join(mounthdir, mailfn)
            mail = Email(mailfile).load()
            if mail.valid:
                key = (mail.timestamp, mail.sujet)
                if key not in dedup:
                    dedup[key] = mail.mailfile
                    yield mail
                else:
                    warning('duplicates {} <-> {}'.format(dedup[key], mailfile))
