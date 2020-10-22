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

    def __init__(self, file):
        self.file = file
        self.doc_map = {} # key: docId, value: (title, abstract)
        self.terms = {} # key: docId, value: list of terms

    def readTokens(self):
        doc_list = CorpusReader.CorpusReader(self.file).readCorpus()
        for (sha, title, abst) in doc_list:
            self.doc_map[sha] = (title, abst)


class SimpleTokenizer(Tokenizer):

    def __init__(self, file):
        super().__init__(file)

    def readTokens(self):
        super().readTokens()

    def createTerms(self):
        for docId in self.doc_map.keys():
            # replaces all non-alphabetic characters by a space, lowercases tokens, splits on whitespace
            self.terms[docId] = re.split('[\s]', re.sub(r'[^A-Za-z]', ' ', self.doc_map[docId][0] + " "
                                                                                + self.doc_map[docId][1])
                                                        .lower())
            # ignores all tokens with less than 3 characters
            self.terms[docId] = list(filter(lambda term: len(term) >= 3, self.terms[docId]))

    def getTokens(self):
        return self.terms


class BetterTokenizer(Tokenizer):

    def __init__(self, file):
        super().__init__(file)

    def readTokens(self):
        super().readTokens()

    def createTerms(self):
        for docId in self.doc_map.keys():
            # TODO: better changes and splits
            pass
        self.stopWordFilter()
        self.stem()

    def stopWordFilter(self):
        # get the english stopwords
        stopwords = ""
        with open('snowball_stopwords_EN.txt', 'r') as document:
            stopwords += list(filter(None,re.split("[ \n]", document.read())))
        document.close()
        self.terms = list(filter(lambda term: term not in stopwords, self.terms))

    def stem(self):
        stemmer = Stemmer.Stemmer('english')
        self.terms = stemmer.stemWords(self.terms)

    def getTokens(self):
        return self.terms
