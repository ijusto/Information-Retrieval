class Indexer:

    def __init__(self, pairs, numDocs):
        self.pairs = pairs
        # key: docId, value: list of 10 most frequent terms
        self.tenMostFreqTerms = {}
        # { docId : { term : freq } }
        self.freqDict = {}
        self.numDocs = numDocs

    def indexTerms(self, letterLimit):
        # sort by terms and then sort by docId for the same terms
        self.pairs = sorted(self.pairs, key=lambda p: (p[0], p[1]))

        # initialize dictionaries of key:term, value: frequency for each document
        for docId in range(self.numDocs):
            self.freqDict[docId] = {}

        # initialize the frequency of each term to 0
        for (term, docId) in self.pairs:
            self.freqDict[docId][term] = 0

        # count the frequency of the terms in each document
        for (term, docId) in self.pairs:
            self.freqDict[docId][term] += 1

        # sort by frequency
        for docId in range(self.numDocs):
            self.tenMostFreqTerms[docId] = [term for term in
                                                sorted(self.freqDict[docId], key=lambda d: self.freqDict[docId][d],
                                                                             reverse=True)
                                                if letterLimit == None or len(term) >= letterLimit][0:10]

    def getFreqTerms(self):
        return self.tenMostFreqTerms