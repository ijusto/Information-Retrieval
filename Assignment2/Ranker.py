# Ranker
#  Scores all retrieved documents according to a relevance metric.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

from ScoreCalculations import *


class Ranker:

    # The constructor.
    #  @param self The object pointer.
    def __init__(self, documentsInfo):
        self.documentsInfo = documentsInfo  # {docId: {term: (term_idf, logWeight)}}

    def lnc_ltc(self):
        documentScore = {}  # {docId: lnc_ltc}

        queriesWeights = {}  # {term: ltc_weight}
        documentsWeights = {}  # {docId: {term: lnc_weight}}

        # lnc
        # logarithmic weight
        for docId, termsInfo in self.documentsInfo.items():
            documentsWeights[docId] = {}
            for term, (idf, logWeight) in termsInfo.items():
                if term not in queriesWeights.keys():
                    queriesWeights[term] = (idf, logWeight)
                documentsWeights[docId][term] = logWeight

        # cosine normalization
        for docId, termsInfo in self.documentsInfo.items():
            docWeights = [lnc_weight for term, lnc_weight in termsInfo.items()]
            for term, _ in termsInfo.items():
                documentsWeights[docId][term] /= getDocL2Norm(docWeights)

        # ltc
        # tfidf
        for term, (idf, logWeight) in queriesWeights.keys():
            queriesWeights[term] = logWeight * idf

        # cosine normalization
        tf_idfs = queriesWeights.values()
        for term, tf_idf in queriesWeights.keys():
            queriesWeights[term] = tf_idf / getDocL2Norm(tf_idfs)

        # lnc-ltc
        for docId, termsInfo in self.documentsInfo.items():
            documentScore[docId] = sum([lnc_weight * queriesWeights[term] for term, lnc_weight in termsInfo.items()])

        #return dict(sorted(documentScore.items(), key=lambda items: items[1]))

    def bm25(self, lenD, avgdl, k1=1.2, b=0.75):
        # {docId: bm25}
        documentScore = {docId: sum([idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (lenD / avgdl))))
                                     for _, (idf, tf) in termsInfo.items()])
                         for docId, termsInfo in self.documentsInfo.items()}
        #return dict(sorted(documentScore.items(), key=lambda items: items[1]))
