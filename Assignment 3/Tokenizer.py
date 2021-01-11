# Tokenizer
#  Forms index words (terms).
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import re
import Stemmer
import timeit

class Tokenizer:

    # The constructor.
    #  @param self The object pointer.
    #  @param text Text in the document
    def __init__(self, text):
        self.text = text

    def changeText(self, text):
        self.terms = []
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
    #  @param withPositions todo
    #  @returns the list of terms in this document.
    def getTerms(self, withPositions=False):
        # replaces all non-alphabetic characters by a space, lowercase tokens, splits on whitespace
        self.terms = re.split('[\s]', re.sub(r'[^A-Za-z]', ' ', self.text)
                              .lower())

        # ignores all tokens with less than 3 characters
        self.terms = list(filter(lambda term: len(term) >= 3, self.terms))

        # remove duplicates
        res = []
        _ = [res.append(term) for term in self.terms if term not in res]
        self.terms = res
        del res

        if withPositions:
            text = re.split('[\s]', self.text)
            termsPositions = []
            for pos in range(len(text)):
                if text[pos] in self.terms:
                    if text[pos] not in termsPositions:
                        termsPositions += [pos]
                    else:
                        termsPositions[termsPositions.index(text[pos])] += [pos]
            return self.terms, termsPositions

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
    #  @param withPositions todo
    #  @returns the list of terms in this document.
    def getTerms(self, withPositions=False):
        start = timeit.default_timer()

        # split by whitespace
        terms = re.split('[\s]', self.text)

        stemmer = Stemmer.Stemmer('english')
        # get the english stopwords
        stopwords = []
        with open('snowball_stopwords_EN.txt', 'r') as document:
            stopwords += list(filter(None, re.split("[ \n]", document.read())))
        document.close()

        if withPositions:
            termsPositions = []  # [[term0pos0, term0pos1,...], [term1pos0, term1pos1, term1pos2]

        for pos in range(len(terms)):

            # in case there is more than one term in this split by whitespace list position
            tempTermList = []

            # maintain websites
            url_match = re.findall(
                r'(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9'
                r'][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|ww'
                r'w\.[a-zA-Z0-9]+\.[^\s]{2,})', terms[pos])
            # maintain emails
            email_match = re.findall(r'[\w.-]+@[\w.-]+', terms[pos])
            # maintain words with hyphens
            hyphen_match = re.findall(r"([A-Za-z]+-[A-Za-z]+)", terms[pos])
            # maintain apostrophes
            apostrophe_match = re.findall(r"([A-Za-z]+'[A-Za-z]*)", terms[pos])
            # maintain acronyms
            acronyms_match = re.findall(r'\b(?:[a-zA-Z]\.){2,}', terms[pos])
            # maintain siglas
            siglas_match = re.findall(r'\b(?:[A-Z]){2,}', terms[pos])

            if url_match:
                if url_match[0].endswith(').') or url_match[0].endswith('),'):
                    url_match = [url_match[0][:-2]]  # ex: https://www.genomedetective.com/app/typingtool/cov).
                elif url_match[0].endswith(',') or url_match[0].endswith('.') or url_match[0].endswith(')') or \
                        url_match[0].endswith('}'):
                    url_match = [url_match[0][:-1]]
                tempTermList = url_match
            elif email_match:
                tempTermList = email_match
            elif hyphen_match:
                tempTermList = hyphen_match
            elif apostrophe_match:
                if apostrophe_match[0].endswith('\''):
                    apostrophe_match = [apostrophe_match[0][:-1]]
                tempTermList = apostrophe_match
            elif acronyms_match:
                tempTermList = acronyms_match
            elif siglas_match:
                tempTermList = siglas_match
            else:
                # remove html character entities, ex: &nbsp;
                term = re.sub(r'(&.+;)', '', terms[pos])

                # replaces all non-alphabetic characters by a space, lowercases term, splits on whitespace
                tempTermList = re.split('[\s]', re.sub(r'[^A-Za-z]', ' ', term).lower())

            while ('' in tempTermList):
                tempTermList.remove('')

            # Removes stopwords from the list of the terms of the document.
            tempTermList = list(filter(lambda term: term not in stopwords, tempTermList))
            # Stemmes
            tempTermList = [stemmer.stemWord(term) for term in tempTermList]
            # ignores all tokens with less than 3 characters
            tempTermList = list(filter(lambda t: len(t) >= 3, tempTermList))

            if tempTermList != []:
                if withPositions: # [[term0pos0, term0pos1,...], [term1pos0, term1pos1, term1pos2]
                    for termInd in range(len(tempTermList)):
                        if tempTermList[termInd] in self.terms:
                            termsPositions[self.terms.index(tempTermList[termInd])] += [pos]
                        else:
                            self.terms += [tempTermList[termInd]]
                            termsPositions += [[pos]]
                else:
                    self.terms += [term for term in tempTermList if term not in self.terms]

        if withPositions:
            stop = timeit.default_timer()
            print('getTerms: {} seconds'.format(stop - start))
            return self.terms, termsPositions

        stop = timeit.default_timer()
        print('getTerms: {} seconds'.format(stop - start))
        return self.terms
