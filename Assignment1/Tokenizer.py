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
        for docId in self.doc_map.keys():
            # split by whitespace
            self.terms[docId] = re.split('[\s]', self.doc_map[docId][0] + " " + self.doc_map[docId][1])

            # dealing with pontuation except the (.), (-), (@), (/) and (') - deal with emails, hyphen words, prime words and websites (NOT COMPLETED)
            self.terms[docId] =  re.sub(r'[\!\"\#\$\%\&\(\)\*\+\,\:\;\<\>\=\?\[\]\{\}\\\\\^\_\`\~]+', '',  self.doc_map[docId][0])

            # dealing with prime (') (NOT COMPLETED)
            self.terms[docId] =  re.sub(r'[\']', '',  self.doc_map[docId][0])
            
            # dealing with websites (/ : .) ATENTION to special characters in links (NOT COMPLETED)
            self.terms[docId] =  re.sub(r'[(https?:\/\/)?(www\.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)|(https?:\/\/)?(www\.)?(?!ww)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)]', '',  self.doc_map[docId][0])

            
            # dealing with emails (NOT COMPLETED)
            self.terms[docId] =  re.sub(r'[\']', '',  self.doc_map[docId][0])

            # DEAL with this type of situations:
            # Finland's  isn't  Passengers'  porta-voz  Coronavirus:   2019-2020  (Whuan)  COVID-19
            # (qwerty):   Sars-COV-2   health - The   "Anxiety..."    receptor-independent -dependent


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
