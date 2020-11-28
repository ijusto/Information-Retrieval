# Query Operations
#  Transforms the query to improve retrieval.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import Tokenizer

def getQueriesTerms(tokenizerType, query):
    if tokenizerType == '0':  # simple
        tokenizer = Tokenizer.SimpleTokenizer(query.replace('\n', ' '))
    else:  # better
        tokenizer = Tokenizer.BetterTokenizer(query.replace('\n', ' '))

    return tokenizer.getTerms()