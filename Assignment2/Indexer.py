# Indexer.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import CorpusReader
import Tokenizer
import timeit
import psutil
import os
import math

# Indexer
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
        self.dictStr = ""
        # list of dictionaries {docId: term_freq} for each term (postings with term_freq), (length = number of terms)
        self.postingsMaps = []
        # list of document frequencies, (length = number of terms)
        #self.docFreq = []
        # list of pointers/indexes to terms in the dictionary string (after blocking, length < number of terms)
        # with blocking
        self.termPtrs = []
        # list of pointers/indexes in postingsMaps
        # TODO: Gamma encoding
        self.postingsPtrs = []
        # Blocking parameter in dictionary compression
        self.k = 4
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
        #print('\nVocabulary Size: {}'.format(len(self.docFreq)))


    # Populates the term_map dictionary with another dictionary with doi's as keys and the term's frequency in that
    # document
    #  @param self The object pointer.
    def index(self):

        allTerms = []

        collection = CorpusReader.CorpusReader(self.collectionPath).readCorpus()  # list((doi, title, abstract))
        self.N = len(collection)
        for doi, title, abstract in collection:
            if self.tokenizerType == '0':  # simple
                tokenizer = Tokenizer.SimpleTokenizer(title, abstract)
            else:  # better
                tokenizer = Tokenizer.BetterTokenizer(title, abstract)

            terms = tokenizer.getTerms()

            for term in terms:
                if term in allTerms:
                    if doi in self.postingsMaps[allTerms.index(term)].keys():
                        self.postingsMaps[allTerms.index(term)][doi] += 1
                    else:
                        # self.docFreq[allTerms.index(term)] += 1
                        self.postingsMaps[allTerms.index(term)][doi] = 1
                else:
                    allTerms += [term]
                    self.postingsPtrs += [len(allTerms) - 1]
                    term_freq_map = {doi: 1}  # key: docId, value: term_freq
                    self.postingsMaps += [term_freq_map]
                    # self.docFreq += [1]

        self.dictionaryCompression(allTerms)


    # The search begins with the dictionary.
    # We want to keep it in memory .
    # Even if the dictionary isn't in memory, we want it to be small for a fast search start up time
    def dictionaryCompression(self, allTerms):

        # terms in alphabetical order
        self.postingsMaps = sortListByTerms(allTerms, self.postingsMaps)
        #self.docFreq = sortListByTerms(allTerms, self.docFreq)
        self.postingsPtrs = sortListByTerms(allTerms, self.postingsPtrs)
        terms = sorted(allTerms)
        # store dictionary as a (long) string of characters with the length of each term preceding it
        self.dictStr = ""
        # front coding - sorted words commonly have long common prefix-store differences only
        # example: 8automata8automate9automatic10automation  becomes: 8automat*a1|e2|ic3|ion
        encodedTerm = ""
        # TODO: check if remove * and | from tokenizer

        for i in range(len(terms)):
            # Blocking of k = 4 (store pointers to every 4th term strings)
            if (i % 4) == 0:
                # Because there is no pointers in python, we store the position of the length of the term in the string
                # as a pointer to were the term is located in the string
                termPtr = len(self.dictStr)
                self.termPtrs += [termPtr]

            lenTerm = str(len(terms[i]))
            prefixLen = 0
            # last term had a prefix common with another term, and the current one starts with that same prefix
            if encodedTerm != "" and terms[i].startswith(encodedTerm):
                # extraLength | remainPartOfTheTerm, e.g.: 1|e
                self.dictStr += str(len(terms[i][len(encodedTerm):])) + "|" + terms[i][len(encodedTerm):]
            # last term and the current one have no common prefix
            elif i <= len(terms) - 2:
                # e.g.: 8
                self.dictStr += lenTerm
                # evaluate if there is a common prefix with the next term
                while True:
                    if prefixLen == len(terms[i]) or terms[i][prefixLen] != terms[i + 1][prefixLen]:
                        break
                    prefixLen += 1
                # only encode terms with common prefixes with more than 3 characters
                if prefixLen > 3:
                    encodedTerm = terms[i][:prefixLen]
                    self.dictStr += encodedTerm + '*' + terms[i][prefixLen:]
                else:
                    self.dictStr += terms[i]
                    encodedTerm = ""
            # last term with no shared prefix
            else:
                self.dictStr += lenTerm + terms[i]
                encodedTerm = ""

    def getTermsFromDictStr(self) -> list:
        terms = []

        for ptrInd in range(len(self.termPtrs)):
            # Blocking of k = 4 (store pointers to every 4th term strings)
            termPtr = self.termPtrs[ptrInd]
            for i in range(4):
                if termPtr >= len(self.dictStr):
                    break
                lenInPtrStr = ""
                nDigitLen = 0
                while True:
                    lenInPtrStr += self.dictStr[termPtr + nDigitLen]
                    nDigitLen += 1
                    if not self.dictStr[termPtr + nDigitLen].isdigit():
                        nDigitLen -= 1
                        break
                lenInPtr = int(lenInPtrStr)

                newPtr = termPtr + nDigitLen
                extraLength = lenInPtr if self.dictStr[newPtr + 1] == '|' else 0

                if extraLength == 0:
                    term = self.dictStr[newPtr + 1:newPtr + 1 + lenInPtr]

                    termPtr = newPtr + 1 + lenInPtr
                    if '*' in term:
                        term = term.replace('*', '')
                        # Discover extra part of the word
                        term += self.dictStr[newPtr + 1 + lenInPtr]
                        termPtr += 1
                    elif newPtr + 1 + lenInPtr < len(self.dictStr) - 1 and '*' in self.dictStr[newPtr + 1 + lenInPtr]:
                        termPtr += 1
                else:
                    # Discover base word
                    endBaseWord = 1
                    while True:
                        char = self.dictStr[newPtr - endBaseWord]
                        if char == '*':
                            break
                        endBaseWord += 1

                    startBaseWord = endBaseWord
                    while True:
                        char = self.dictStr[newPtr - startBaseWord]
                        if char.isdigit():
                            startBaseWord -= 1
                            term = self.dictStr[newPtr - startBaseWord: newPtr - endBaseWord]
                            break
                        startBaseWord += 1

                    # Discover extra part of the word
                    term += self.dictStr[newPtr + 2: newPtr + 2 + extraLength]
                    termPtr = newPtr + 2 + extraLength

                terms += [term]

        return terms

    def postingsGammaEncoded(self):
        pass

    # Returns the number of times that the term t occurs in the document d, i.e., the term frequency TF(t,d) of term t
    # in document d
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @param dId The document id.
    #  @returns the term frequency TF(t,d) of term t in document d
    def getTFtd(self, tIndex, dId):
        return self.postingsMaps[tIndex][dId]

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
        return len(list(self.postingsMaps[tIndex].keys()))

    # Returns the inverse document frequency of term t
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @returns idf(t) - the inverse document frequency of term t
    def getIDFt(self, tIndex):
        return math.log10(self.N/self.getDFt(tIndex))

    # Returns the tf-idf weight of a term in a document (W(t,d))
    #  @param self The object pointer.
    #  @param tIndex The term index.
    #  @param dId The document id.
    #  @returns W(t,d) - the term frequency-inverse document frequency weight of term t in document d
    def getTFIDFtWeight(self, tIndex, dId):
        tf = self.getTFtd(tIndex, dId)
        return 0 if tf <= 0 else (1 + math.log10(tf)) * self.getIDFt(tIndex)

    # Lists the ten first terms (in alphabetic order) that appear in only one document (document frequency = 1).
    #  @param self The object pointer.
    def listTermsInOneDoc(self):
        terms = self.getTermsFromDictStr()
        # results = [term for term in sorted(terms) if self.docFreq[terms.index(term)] == 1]
        results = [term for term in sorted(terms) if len(list(self.postingsMaps[terms.index(term)].keys())) == 1]
        print('\nTen first Terms in only 1 document: \n{}'.format(results[:10]))

    # Lists the ten terms with highest document frequency.
    #  @param self The object pointer.
    def listHighestDocFreqTerms(self):
        terms = self.getTermsFromDictStr()
        # doc_freq = sorted(terms, key=lambda term: self.docFreq[terms.index(term)], reverse=True)
        doc_freq = sorted(terms, key=lambda term: len(list(self.postingsMaps[terms.index(term)].keys())), reverse=True)
        print('\nTen terms with highest document frequency: \n{}'.format(doc_freq[:10]))

    # Lists the ten terms with highest frequency in one document.
    #  @param self The object pointer.
    def listHighestOneDocFreqTerms(self):
        terms = self.getTermsFromDictStr()
        doc_freq = sorted(terms, key=lambda term: max(self.postingsMaps[terms.index(term)].values()), reverse=True)
        print('\nTen terms with highest frequency in one document: \n{}'.format(doc_freq[:10]))


def sortListByTerms(allTerms, toBeSorted):
    return [elem for _, elem in sorted(zip(allTerms, toBeSorted))]