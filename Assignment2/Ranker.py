# Ranker
#  Scores all retrieved documents according to a relevance metric.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

from ScoreCalculations import *

class Ranker:

    # The constructor.
    #  @param self The object pointer.
    def __init__(self, documentsInfo):
        self.documentsInfo = documentsInfo # {docId: {term: (term_idf, weight)}}

    def ltc(self):
        pass


    def bm25(self, lenD, avgdl, k1 = 1.2, b = 0.75):
        documentScore = {} # {docId: bm25}
        for docId, termsInfo in self.documentsInfo.items():
            documentScore[docId] = sum([idf*((tf*(k1+1))/(tf + k1 * (1 - b + b * (lenD/avgdl) ))) for _, (idf, tf) in termsInfo.items()])

