# Searcher
#  Retrieves documents that contain a given query term from the inverted index.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

from ScoreCalculations import *

class Searcher:

    # The constructor.
    #  @param self The object pointer.
    def __init__(self, queriesTerms):
        self.queriesTerms = queriesTerms
        self.ltcQueries = [] # list of {termQuery: {docId: ltc_weight}} for each query
        #self.termPtrs = termPtrs
        #self.postingsPtrs = postingsPtrs

    def getQueryScoresFromIndexer(self, indexFile):
        with open(indexFile, 'r') as f:
            line = f.readline()
            while line != '':
                info = line.split(';')
                term, term_idf = info[0].split(':')

                for queryIndex in range(len(self.queriesTerms)):
                    self.ltcQueries += [{}]
                    for termQuery in self.queriesTerms[queryIndex]:
                        if termQuery == term:
                            self.ltcQueries[queryIndex][termQuery] = {}
                            for doc in info[1:]:
                                docid, tf = doc.split(':')
                                self.ltcQueries[queryIndex][termQuery][docid] = getTFIDFtWeightQuery(tf, term_idf)  # lt
                line = f.readline()
        f.close()

        # cosine normalization
        for queryIndex in range(len(self.queriesTerms)):
            self.ltcQueries[queryIndex] = {term: {docId: self.ltcQueries[queryIndex][term][docId] / getDocL2Norm(docId, self.ltcQueries[queryIndex]) # ltc
                                                for docId in self.ltcQueries[queryIndex][term].keys()}
                                                for term in self.ltcQueries[queryIndex].keys()}


    # def searchForTermInDictionary(self, t):
    #     for ptrInd in range(len(self.termPtrs)):
    #         blockPtr = self.termPtrs[ptrInd]
    #         baseWord = ""
    #         termPtr = blockPtr
    #         lenInPtrStr = ""
    #         nDigitLen = 0
    #         while True:
    #             lenInPtrStr += self.dictionary[termPtr + nDigitLen]
    #             nDigitLen += 1
    #             if not self.dictionary[termPtr + nDigitLen].isdigit():
    #                 nDigitLen -= 1
    #                 break
    #         lenInPtr = int(lenInPtrStr)
    #
    #         newPtr = termPtr + nDigitLen
    #
    #         term = self.dictionary[newPtr + 1:newPtr + 1 + lenInPtr]
    #
    #         termPtr = newPtr + 1 + lenInPtr
    #         if '*' in term:
    #             term = term.replace('*', '')
    #             # Discover extra part of the word
    #             term += self.dictionary[newPtr + 1 + lenInPtr]
    #             termPtr += 1
    #         elif newPtr + 1 + lenInPtr < len(self.dictionary) - 1 and '*' in self.dictionary[newPtr + 1 + lenInPtr]:
    #             termPtr += 1
