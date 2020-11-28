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
        self.documentsInfo = {} # {docId: {term: (term_idf, logWeight)}}
        #self.termPtrs = termPtrs
        #self.postingsPtrs = postingsPtrs

    def searchDocuments(self, indexFile):
        with open(indexFile, 'r') as f:
            line = f.readline()
            while line != '':
                info = line.split(';')
                term, term_idf = info[0].split(':')

                for termQuery in self.queriesTerms:
                    if termQuery == term:
                        for doc in info[1:]:
                            docId, logWeight = doc.split(':')
                            if docId not in self.documentsInfo.keys():
                                self.documentsInfo[docId] = {}
                            self.documentsInfo[docId][termQuery] = (term_idf, logWeight)
                line = f.readline()
        f.close()

        return self.documentsInfo

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
