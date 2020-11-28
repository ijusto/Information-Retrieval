# Query Operations
#  Transforms the query to improve retrieval.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import Tokenizer

class QueryOperations:

    # The constructor.
    #  @param self The object pointer.
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, tokenizerType, query):
        self.tokenizerType = tokenizerType
        self.query = query

    def getQueriesTerms(self):
        if self.tokenizerType == '0':  # simple
            tokenizer = Tokenizer.SimpleTokenizer(self.query.replace('\n', ' '))
        else:  # better
            tokenizer = Tokenizer.BetterTokenizer(self.query.replace('\n', ' '))

        return tokenizer.getTerms()