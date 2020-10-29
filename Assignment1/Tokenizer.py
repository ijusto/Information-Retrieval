# 2. Create two tokenizers:
#   i. A simple tokenizer that replaces all non-alphabetic characters by a space, lowercases tokens, splits on
#       whitespace, and ignores all tokens with less than 3 characters.
#   ii. An improved tokenizer that incorporates your own tokenization decisions (e.g. how to deal with digits and
#       characters such as ’, -, @, etc).
#       Integrate the Porter stemmer (http://snowball.tartarus.org/download.html) and a stopword filter. Use this list
#       as default: https://bit.ly/2kKBCqt

import re
import CorpusReader
import Stemmer

class Tokenizer:

    def __init__(self, title, abstract):
        self.title = title
        self.abstract = abstract
        self.terms = []


class SimpleTokenizer(Tokenizer):

    def __init__(self, title, abstract):
        super().__init__(title, abstract)

    def getTerms(self):
        # replaces all non-alphabetic characters by a space, lowercases tokens, splits on whitespace
        self.terms = re.split('[\s]', re.sub(r'[^A-Za-z]', ' ', self.title + " " + self.abstract)
                              .lower())
        # ignores all tokens with less than 3 characters
        self.terms = list(filter(lambda term: len(term) >= 3, self.terms))

        return self.terms


class BetterTokenizer(Tokenizer):

    def __init__(self, title, abstract):
        super().__init__(title, abstract)

    def getTerms(self):
        # split by whitespace
        self.terms = re.split('[\s]', self.title + " " + self.abstract)

        # ignore websites
        self.terms = [term for term in self.terms if not re.match(r'(https?:\/\/)?(www\.)[-a-zA-Z0-9@:%._\+~#=]{2,256}'
                                                                  r'\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)|(https'
                                                                  r'?:\/\/)?(www\.)?(?!ww)[-a-zA-Z0-9@:%._\+~#=]{2,256}'
                                                                  r'\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', term)
                      # ignore emails
                      and not re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', term)
                      # ignore words with hyphens and aphostrophes and both
                      # 's, yea', don't, -yeah, no-, ice-cream, Qu'est-ce, Mary's, High-school, 'tis, Chambers',
                      # Qu'est-ce, Finland's, isn't, Passengers'
                      # 2019-2020, COVID-19, receptor-independent
                      and not re.match(r"'?\w[\w']*(?:-\w+)*'?", term)]

        # dealing with extra pontuation and symbols
        # ignoring (_) for this type of situation NC_004718.3
        self.terms = [re.sub(r'[\!\"\#\$\%\&\(\)\*\+\,\:\.\-\'\_\\\/\;\<\>\=\?\[\]\{\}\\\^\`\~\±0-9]+', '', term)
                      for term in self.terms]

        self.stopWordFilter()
        self.stem()
        print(self.terms)
        return self.terms

    def stopWordFilter(self):
        # get the english stopwords
        stopwords = []
        with open('snowball_stopwords_EN.txt', 'r') as document:
            stopwords += list(filter(None, re.split("[ \n]", document.read())))
        document.close()
        self.terms = list(filter(lambda term: term not in stopwords, self.terms))

    def stem(self):
        stemmer = Stemmer.Stemmer('english')
        self.terms = stemmer.stemWords(self.terms)
