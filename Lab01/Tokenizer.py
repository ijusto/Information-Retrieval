import re

class Tokenizer:

    def __init__(self, file):
        self.file = file
        self.terms = []

    def createTokens(self):
        # Tokenization
        with open(self.file, 'r') as document:
            tokens = list(filter(None,re.split("[.!?\\- ,\n<>«»{}=\"$0-9()*;#%&'+/:|]", document.read())))
        document.close()

        # get the portuguese stopwords
        with open('stopwords.txt', 'r') as document:
            stopwords = list(filter(None,re.split("[ \n]", document.read())))
        document.close()

        # get the english stopwords
        with open('stopwords_en.txt', 'r') as document:
            stopwords += list(filter(None,re.split("[ \n]", document.read())))
        document.close()

        for token in tokens:
            #  ommit very common words
            if token.lower() not in stopwords:
                # apply linguistic module
                self.terms += [token.lower()]

    def getTokens(self):
        return self.terms
