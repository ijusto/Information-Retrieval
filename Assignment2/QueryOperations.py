# Query Operations
#  Transforms the query to improve retrieval.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import Tokenizer

class QueryOperations:

    # The constructor.
    #  @param self The object pointer.
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, tokenizerType):
        self.tokenizerType = tokenizerType

    def getQuery(self, query):
        if self.tokenizerType == '0':  # simple
            tokenizer = Tokenizer.SimpleTokenizer(query)
        else:  # better
            tokenizer = Tokenizer.BetterTokenizer(query)

        qTerms = tokenizer.getTerms()
