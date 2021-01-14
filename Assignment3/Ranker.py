# Ranker
#  Scores all retrieved documents according to a relevance metric.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

from ScoreCalculations import *


class Ranker:

    # The constructor.
    #  @param self The object pointer.
    def __init__(self, documentsInfo, avgDocLen):
        self.documentsInfo = documentsInfo  # {docId: lenD, {term: (term_idf, logWeight)}}
        self.avgDocLen = avgDocLen

    # Check term proximity score of every 2 co-occurring terms in the query
    def check_proximity(self, term1, term2, docId):
        total_score = 0.0
        pos_list1 = []
        pos_list2 = []
        pos_list1 = self.documentsInfo[docId][2][term1][3]
        pos_list2 = self.documentsInfo[docId][2][term2][3]

        for pos in pos_list1:
            termscore = 0.0
            if pos + 1 in pos_list2:
                termscore = 1.0
            elif pos + 2 in pos_list2:
                termscore = 0.95
            elif pos + 3 in pos_list2:
                termscore = 0.9
            elif pos + 4 in pos_list2:
                termscore = 0.60
            total_score += termscore
        print('Proximity total score: {}%'.format(total_score))
        return total_score  # the score of 2 co-occurring terms

    # Calculate the proximity score for every 2 terms in the query    
    def proximity_boost(self, scoreDict, queryTerms):
        proximity_score = {}  # dictionary that contains the docId and its proximity score
        tp_score = {}  # term proximity score
        tp_score = scoreDict
        lamb = 0.192  # lambda value for smoothing the proximity score
        for term in range(len(queryTerms) - 1):
            q1 = queryTerms[term]
            q2 = queryTerms[term + 1]
            proximity_terms = queryTerms[term:term + 2]
            if (proximity_terms[0] in self.documentsInfo) & (proximity_terms[1] in self.documentsInfo):
                doc = []
                for docId in self.documentsInfo[proximity_terms[0]]:
                    score = 0
                    if docId in self.documentsInfo[proximity_terms[1]]:
                        score = self.check_proximity(proximity_terms[0], proximity_terms[1],
                                                     docId)
                    try:
                        proximity_score[docId] += score
                    except KeyError:
                        proximity_score[docId] = score
        for k, v in proximity_score.items():
            doclen = self.avgDocLen[k]  # document's length
            proximity_smoothing = lamb * v  # proximity smoothing
            scoreDict_smoothing = (1 - lamb) * scoreDict[k]  # scoreDict smoothing
            tp_score[k] = scoreDict_smoothing + proximity_smoothing
        tp_sort_dict = sorted(tp_score.items(), key=lambda items: items[1], reverse=True)
        return dict(tp_sort_dict)
        # form_the_file(qid, tp_sort_dict)

    def lnc_ltc(self):
        documentScore = {}  # {docId: lnc_ltc}

        queriesWeights = {}  # {term: ltc_weight}
        documentsWeights = {}  # {docId: {term: lnc_weight}}

        # lnc
        # logarithmic weight
        for docId, (_, termsInfo) in self.documentsInfo.items():
            documentsWeights[docId] = {}
            for term, (idf, logWeight, _) in termsInfo.items():
                if term not in queriesWeights.keys():
                    queriesWeights[term] = (idf, logWeight, _)
                documentsWeights[docId][term] = logWeight

        # cosine normalization
        for docId in documentsWeights.keys():
            docWeights = documentsWeights[docId].values()
            for term in documentsWeights[docId].keys():
                documentsWeights[docId][term] /= getDocL2Norm(docWeights)

        # ltc
        # tfidf
        for term, (idf, logWeight, _) in queriesWeights.items():
            queriesWeights[term] = logWeight * idf

        # cosine normalization
        tf_idfs = queriesWeights.values()
        for term, tf_idf in queriesWeights.items():
            queriesWeights[term] = tf_idf / getDocL2Norm(tf_idfs)

        # lnc-ltc
        for docId in documentsWeights.keys():
            documentScore[docId] = sum(
                [lnc_weight * queriesWeights[term] for term, lnc_weight in documentsWeights[docId].items()])

        return dict(sorted(documentScore.items(), key=lambda items: items[1], reverse=True))

    def bm25(self, k1=1.2, b=0.75):
        # {docId: bm25}
        documentScore = {docId: sum([idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (lenD / self.avgDocLen))))
                                     for _, (idf, tf) in termsInfo.items()])
                         for docId, (lenD, termsInfo) in self.documentsInfo.items()}

        return dict(sorted(documentScore.items(), key=lambda items: items[1], reverse=True))
