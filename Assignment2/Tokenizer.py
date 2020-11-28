# Tokenizer
#  Forms index words (terms).
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import re
import Stemmer


class Tokenizer:

    # The constructor.
    #  @param self The object pointer.
    #  @param text Text in the document
    def __init__(self, text):
        self.text = text


# A simple tokenizer that replaces all non-alphabetic characters by a space, lowercase tokens, splits on  whitespace,
#  and ignores all tokens with less than 3 characters.
class SimpleTokenizer(Tokenizer):

    # The constructor.
    #  @param self The object pointer.
    #  @param text Text in the document
    def __init__(self, text):
        super().__init__(text)
        self.terms = []

    # Populates the terms list with the terms in the document.
    #  @param self The object pointer.
    #  @returns the list of terms in this document.
    def getTerms(self):
        # replaces all non-alphabetic characters by a space, lowercase tokens, splits on whitespace
        self.terms = re.split('[\s]', re.sub(r'[^A-Za-z]', ' ', self.text)
                              .lower())
        # ignores all tokens with less than 3 characters
        self.terms = list(filter(lambda term: len(term) >= 3, self.terms))

        return self.terms


# An improved tokenizer that incorporates more tokenization decisions than the SimpleTokenizer and integrates the
#  Porter stemmer (http://snowball.tartarus.org/download.html) and a stop word filter. «
class BetterTokenizer(Tokenizer):

    # The constructor.
    #  @param self The object pointer.
    #  @param text Text in the document
    def __init__(self, text):
        super().__init__(text)
        self.terms = []

    # Populates the terms list with the terms in the document.
    #  @param self The object pointer.
    #  @returns the list of terms in this document.
    def getTerms(self):
        # split by whitespace
        terms = re.split('[\s]', self.text)
        print(self.text, terms)
        for term in terms:
            # maintain websites
            url_match = re.findall(
                r'(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9'
                r'][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|ww'
                r'w\.[a-zA-Z0-9]+\.[^\s]{2,})', term)
            # maintain emails
            email_match = re.findall(r'[\w.-]+@[\w.-]+', term)
            # maintain words with hyphens
            hyphen_match = re.findall(r"([A-Za-z]+-[A-Za-z]+)", term)
            # maintain apostrophes
            apostrophe_match = re.findall(r"([A-Za-z]+'[A-Za-z]*)", term)
            # maintain acronyms
            acronyms_match = re.findall(r'\b(?:[a-zA-Z]\.){2,}', term)
            # maintain siglas
            siglas_match = re.findall(r'\b(?:[A-Z]){2,}', term)

            if url_match:
                if url_match[0].endswith(').') or url_match[0].endswith('),'):
                    url_match = [url_match[0][:-2]]  # ex: https://www.genomedetective.com/app/typingtool/cov).
                elif url_match[0].endswith(',') or url_match[0].endswith('.') or url_match[0].endswith(')'):
                    url_match = [url_match[0][:-1]]
                self.terms += url_match
            elif email_match:
                self.terms += email_match
            elif hyphen_match:
                self.terms += hyphen_match
            elif apostrophe_match:
                if apostrophe_match[0].endswith('\''):
                    apostrophe_match = [apostrophe_match[0][:-1]]
                self.terms += apostrophe_match
            elif acronyms_match:
                self.terms += acronyms_match
            elif siglas_match:
                self.terms += siglas_match
            else:
                # remove html character entities, ex: &nbsp;
                self.terms += [re.sub(r'(&.+;)', '', term)]

                # replaces all non-alphabetic characters by a space, lowercases term, splits on whitespace
                self.terms = re.split('[\s]', re.sub(r'[^A-Za-z]', ' ', term).lower())

        self.stopWordFilter()
        self.stem()
        self.terms = list(filter(lambda t: len(t) >= 3, self.terms))
        return self.terms

    # Removes stopwords from the list of the terms of the document.
    #  @param self The object pointer.
    def stopWordFilter(self):
        # get the english stopwords
        stopwords = []
        with open('snowball_stopwords_EN.txt', 'r') as document:
            stopwords += list(filter(None, re.split("[ \n]", document.read())))
        document.close()
        self.terms = list(filter(lambda term: term not in stopwords, self.terms))

    # Stemmes the the list of the terms of the document.
    #  @param self The object pointer.
    def stem(self):
        stemmer = Stemmer.Stemmer('english')
        self.terms = stemmer.stemWords(self.terms)
