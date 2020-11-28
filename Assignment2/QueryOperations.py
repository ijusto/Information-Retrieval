# Query Operations
#  Transforms the query to improve retrieval.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import Tokenizer

class QueryOperations:

    # The constructor.
    #  @param self The object pointer.
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, tokenizerType, queriesFile):
        self.tokenizerType = tokenizerType
        self.queriesFile = queriesFile
        self.queries = []

    def readQueries(self):
        f = open(self.queriesFile, 'r')
        self.queries = f.readlines()
        f.close()

    def getQueriesTerms(self):
        queriesTerms = []
        for query in self.queries:
            if self.tokenizerType == '0':  # simple
                tokenizer = Tokenizer.SimpleTokenizer(query.replace('\n', ' '))
            else:  # better
                tokenizer = Tokenizer.BetterTokenizer(query.replace('\n', ' '))

            queriesTerms += tokenizer.getTerms()

        return queriesTerms