# Ranker
#  Scores all retrieved documents according to a relevance metric.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import math

class Ranker:

    # The constructor.
    #  @param self The object pointer.
    def __init__(self, N):
        self.N = N

    def bm25(self, d, q, lenD, avgdl, k1 = 1.2, b = 0.75):
        return sum([self.getIDFt(qi)*((self.getTFtd(qi, d)*(k1+1))/(self.getTFtd(qi, d) + k1 * (1 - b + b * (lenD/avgdl) ))) for qi in q])

    # Returns the inverse document frequency of term t
    #  @param self The object pointer.
    #  @param t The term.
    #  @returns idf(t) - the inverse document frequency of term t
    def getIDFt(self, t):
        return math.log10(self.N / self.getDFt(t))

    # Returns the number of times that the term t occurs in the document d, i.e., the term frequency TF(t,d) of term t
    # in document d
    #  @param self The object pointer.
    #  @param t The term.
    #  @param dId The document id.
    #  @returns the term frequency TF(t,d) of term t in document d
    def getTFtd(self, t, d):
        pass

    # Returns the number of documents that contain the term t
    #  @param self The object pointer.
    #  @param t The term.
    #  @returns df(t) - the document frequency of term t
    def getDFt(self, t):
        pass
