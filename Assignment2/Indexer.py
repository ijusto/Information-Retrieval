# Indexer.
#  Constructs an inverted index of word (term) to document pointers.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import CorpusReader
import Tokenizer
import timeit
import psutil
import os
import math


# Indexer
from GammaEncoder import GammaEncoder
from Searcher import Searcher


class Indexer:

    # The constructor.
    #  @param self The object pointer.
    #  @param collectionPath The path to the csv containing the collection
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, collectionPath, tokenizerType):
        start = timeit.default_timer()
        self.tokenizerType = tokenizerType
        self.collectionPath = collectionPath

        # store dictionary as a (long) string of characters with the length of each term preceding it
        # front coding
        self.termDictStr = ""
        # Blocking parameter in dictionary compression
        self.k = 4
        # list of pointers/indexes to terms in the dictionary string (after blocking, length < number of terms)
        # with blocking
        self.termPtrs = []

        # dictionary of dictionaries {termInd(PostingPointer): {docId: term_tfidfweigth}} - for each term postings with term_tfidfweigth
        # (length = number of terms)
        self.postingsMaps = {}
        # list of pointers/indexes to postings Lists in the postings string
        self.postingsPtrs = []

        # total number of documents in the collection
        self.N = 0

        self.index()
        stop = timeit.default_timer()

        #   a) What was the total indexing time?
        print('Indexing time - {} tokenizer: {} seconds'.format("simple" if self.tokenizerType == "0" else "better",
                                                                stop - start))

        # How much memory (roughly) is required to index this collection?
        process = psutil.Process(os.getpid())
        print('\nMemory required for indexing: {} MB'.format(process.memory_info().rss / 1000000))  # rss in bytes

        #   b) What is your vocabulary size?
        print('\nVocabulary Size: {}'.format(len(self.postingsMaps)))

        self.searcher = Searcher(self.termDictStr, self.termPtrs, self.postingsPtrs)

    #  todo: description
    #  @param self The object pointer.
    def index(self):

        collection = CorpusReader.CorpusReader(self.collectionPath).readCorpus()  # list((doi, title, abstract))
        self.N = len(collection)

        # first, we populate the dictionary postingsMaps with the term frequency {term_string: {docId: term_freq} }
        for doi, title, abstract in CorpusReader.CorpusReader(self.collectionPath).readCorpus():
            if self.tokenizerType == '0':  # simple
                tokenizer = Tokenizer.SimpleTokenizer(title + " " + abstract)
            else:  # better
                tokenizer = Tokenizer.BetterTokenizer(title + " " + abstract)

            terms = tokenizer.getTerms()

            self.postingsMaps.update({term: {doi: 1 if term not in self.postingsMaps.keys() or doi not in self.postingsMaps[term].keys()
                                                     else self.postingsMaps[term][doi] + 1}
                                                     for term in terms})

        # terms in alphabetical order and docIds ordered
        self.postingsMaps = dict(sorted({term: dict(sorted({doi: term_freq
                                                            for doi, term_freq in self.postingsMaps[term].items()}
                                                           .items())) for term in self.postingsMaps.keys()}.items()))

        # encode the postings and store the pointers
        self.postingsPtrs = GammaEncoder([self.postingsMaps[term].keys() for term in self.postingsMaps.keys()]).encodeAndWritePostings('encodedPostings')

        # we store the terms in a string, the term pointers/indexes of that string in a list, and modify the keys of the
        # postingsMaps to the index of each term if they were on a list alphabetically
        self.dictionaryCompression()

        # lnc (logarithmic term frequency, no document frequency, cosine normalization)
        # then, we modify the postingsMaps from {termInd(PostingPointer): {docId: term_freq}} to
        # {termInd(PostingPointer): {docId: weight}}
        # logarithmic term frequency
        temp = {termInd: {docId: 0 if self.getTFtd(termInd, docId) <= 0
                                                else (1 + math.log10(self.getTFtd(termInd, docId)))
                                                for docId in self.postingsMaps[termInd].keys()}
                                        for termInd in range(len(self.postingsMaps))}
        self.postingsMaps.update(temp)
        # then to {termInd(PostingPointer): {docId: weight (length normalized)}}
        # cosine normalization
        self.postingsMaps = {termInd: {docId: self.postingsMaps[termInd][docId] / self.getDocL2Norm(docId)
                                                for docId in self.postingsMaps[termInd].keys()}
                                        for termInd in range(len(self.postingsMaps))}

    def search(self, term):
        self.searcher.searchForTermInDictionary(term)

    # The search begins with the dictionary.
    # We want to keep it in memory .
    # Even if the dictionary isn't in memory, we want it to be small for a fast search start up time
    def dictionaryCompression(self):
        terms = list(self.postingsMaps.keys())
        # store dictionary as a (long) string of characters with the length of each term preceding it
        self.termDictStr = ""
        # front coding - sorted words commonly have long common prefix-store differences only
        # example: 8automata8automate9automatic10automation  becomes: 8automat*a1|e2|ic3|ion
        encodedTerm = ""
        # TODO: check if remove * and | from tokenizer

        indexInBlock = 0

        for i in range(len(terms)):
            # modify the keys of the postingsMaps to the index of each term if they were on a list alphabetically
            # (postings "pointers"), {termInd(PostingPointer): {docId: term_freq}}
            self.postingsMaps[i] = self.postingsMaps.pop(terms[i])

            lenTerm = str(len(terms[i]))
            prefixLen = 0

            # Front coding in each block of k = 4 (and store pointers to every 4th term strings)
            if indexInBlock == 0:
                indexInBlock = self.k
                # Because there is no pointers in python, we store the position of the length of the term in the string
                # as a pointer to were the term is located in the string
                self.termPtrs += [len(self.termDictStr)]
                encodedTerm = ""

            # last term had a prefix common with another term, and the current one starts with that same prefix
            if encodedTerm != "" and terms[i].startswith(encodedTerm):
                # extraLength | remainPartOfTheTerm, e.g.: 1|e
                self.termDictStr += str(len(terms[i][len(encodedTerm):])) + "|" + terms[i][len(encodedTerm):]
            # last term and the current one have no common prefix
            elif i <= len(terms) - 2:
                # e.g.: 8
                self.termDictStr += lenTerm
                # evaluate if there is a common prefix with the next term
                while True:
                    if prefixLen == len(terms[i]) or terms[i][prefixLen] != terms[i + 1][prefixLen]:
                        break
                    prefixLen += 1
                # only encode terms with common prefixes with more than 3 characters
                if prefixLen > 3:
                    encodedTerm = terms[i][:prefixLen]
                    self.termDictStr += encodedTerm + '*' + terms[i][prefixLen:]
                else:
                    self.termDictStr += terms[i]
                    encodedTerm = ""
            # last term with no shared prefix
            else:
                self.termDictStr += lenTerm + terms[i]
                encodedTerm = ""

    def getTermsFromDictStr(self) -> list:
        terms = []

        for ptrInd in range(len(self.termPtrs)):
            # Blocking of k = 4 (store pointers to every 4th term strings)
            termPtr = self.termPtrs[ptrInd]
            for i in range(4):
                if termPtr >= len(self.termDictStr):
                    break
                lenInPtrStr = ""
                nDigitLen = 0
                while True:
                    lenInPtrStr += self.termDictStr[termPtr + nDigitLen]
                    nDigitLen += 1
                    if not self.termDictStr[termPtr + nDigitLen].isdigit():
                        nDigitLen -= 1
                        break
                lenInPtr = int(lenInPtrStr)

                newPtr = termPtr + nDigitLen
                extraLength = lenInPtr if self.termDictStr[newPtr + 1] == '|' else 0

                if extraLength == 0:
                    term = self.termDictStr[newPtr + 1:newPtr + 1 + lenInPtr]

                    termPtr = newPtr + 1 + lenInPtr
                    if '*' in term:
                        term = term.replace('*', '')
                        # Discover extra part of the word
                        term += self.termDictStr[newPtr + 1 + lenInPtr]
                        termPtr += 1
                    elif newPtr + 1 + lenInPtr < len(self.termDictStr) - 1 and '*' in self.termDictStr[newPtr + 1 + lenInPtr]:
                        termPtr += 1
                else:
                    # Discover base word
                    endBaseWord = 1
                    while True:
                        char = self.termDictStr[newPtr - endBaseWord]
                        if char == '*':
                            break
                        endBaseWord += 1

                    startBaseWord = endBaseWord
                    while True:
                        char = self.termDictStr[newPtr - startBaseWord]
                        if char.isdigit():
                            startBaseWord -= 1
                            term = self.termDictStr[newPtr - startBaseWord: newPtr - endBaseWord]
                            break
                        startBaseWord += 1

                    # Discover extra part of the word
                    term += self.termDictStr[newPtr + 2: newPtr + 2 + extraLength]
                    termPtr = newPtr + 2 + extraLength

                terms += [term]

        return terms

    # Returns the number of times that the term t occurs in the document d, i.e., the term frequency TF(t,d) of term t
    # in document d
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @param dId The document id.
    #  @returns the term frequency TF(t,d) of term t in document d
    def getTFtd(self, tIndex, dId) -> int:
        return 0 if tIndex < 0 else self.postingsMaps[tIndex][dId]

    # Returns the number of occurrences of the term t occurs in the collection, counting multiple occurrences
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @returns the collection frequency of term t
    def getCollectionFreq(self, tIndex):
        return sum([self.postingsMaps[tIndex][docId] for docId in self.postingsMaps[tIndex].keys()])

    # Returns the number of documents that contain the term t
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @returns df(t) - the document frequency of term t
    def getDFt(self, tIndex):
        return 1 if tIndex < 0 else len(list(self.postingsMaps[tIndex].keys()))

    # Returns the inverse document frequency of term t
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @returns idf(t) - the inverse document frequency of term t
    def getIDFt(self, tIndex):
        return math.log10(self.N / self.getDFt(tIndex))

    # Returns the tf-idf weight of a term in a document (W(t,d))
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @param dId The document id.
    #  @returns W(t,d) - the term frequency-inverse document frequency weight of term t in document d
    # todo: before calling this function for queries, verify if the term is in the collection (dictionary)
    #   if not, pass the tIndex = -1
    def getTFIDFtWeight(self, tIndex, dId):
        tf = self.getTFtd(tIndex, dId)
        return 0 if tf == 0 else (1 + math.log10(tf)) * self.getIDFt(tIndex)

    def getDocL2Norm(self, docId):
        return math.sqrt(sum([math.pow(postings[docId], 2) for postings in self.postingsMaps.values()
                              if docId in postings.keys()]))

    def getCosine2Docs(self, docId1, docId2):
        weightsDoc1 = [postings[docId1] for postings in self.postingsMaps.values() if docId1 in postings.keys()]
        weightsDoc2 = [postings[docId2] for postings in self.postingsMaps.values() if docId2 in postings.keys()]
        return sum([w1 * w2 for w1, w2 in zip(weightsDoc1, weightsDoc2)])

