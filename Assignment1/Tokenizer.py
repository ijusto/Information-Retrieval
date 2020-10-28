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

    def readTokens(self, doc_map):
        self.doc_map = doc_map

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
        mail = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        for docId in self.doc_map.keys():   

            # split by whitespace
            self.terms[docId] = re.split('[\s]', self.doc_map[docId][0] + " " + self.doc_map[docId][1])
            
            # ignore websites
            if re.match(r'(https?:\/\/)?(www\.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)|(https?:\/\/)?(www\.)?(?!ww)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', self.doc_map[docId][0]):
                self.terms[docId] = self.doc_map[docId][0]
            
            #ignore emails
            elif re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', self.doc_map[docId][0]): 
                self.terms[docId] = self.doc_map[docId][0]
            
            #ignore words with hyphens and aphostrophes and both
            # 's, yea', don't, -yeah, no-, ice-cream, Qu'est-ce, Mary's, High-school, 'tis, Chambers', Qu'est-ce, Finland's, isn't, Passengers'
            # 2019-2020, COVID-19, receptor-independent
            elif re.match(r"'?\w[\w']*(?:-\w+)*'?", self.doc_map[docId][0]): 
                self.terms[docId] = self.doc_map[docId][0]

            # dealing with extra pontuation and symbols
            # ignoring (_) for this type of situation NC_004718.3
            else:
                self.terms[docId] =  re.sub(r'[\!\"\#\$\%\&\(\)\*\+\,\:\;\<\>\=\?\[\]\{\}\\\^\`\~\±]+', '',  self.doc_map[docId][0])
            
            
        self.stopWordFilter()
        self.stem()
        print(self.terms)

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
