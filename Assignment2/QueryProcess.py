""" # Query Operations
#  Transforms the query to improve retrieval.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import sys
from timeit import default_timer as timer

class QueryProcess:

    # The constructor.
    #  @param self The object pointer.
    #  @param ranktype The type of ranking methods
    def __init__(self, rankType):
        self.rankType = rankType

    def getScores(self, file, rankType):
        
        # Initialization scores dictionary
        scores = dict()
        # Initialization time
        start = []
        end = []
        
        # Read queries
        f = open(file, "r")
        queries = f.read().splitlines()
        f.close()
        
        # If rankType = 0 (tf-idf)
        if rankType == '0':
            for num, query in enumerate(queries):
                
                start.append(timer()) # Start Time for Evaluation
                
                #scores[num] = tf-idf(query) ACABAR FUNÇÃO
                
                end.append(timer()) # End Time for Evaluation
                
        # If rankType = 1 (BM25)
        elif rankType == '1':
            for num, query in enumerate(queries):
                
                start.append(timer()) # Start Time for Evaluation
                
                #scores[num] = bm25(query) ACABAR FUNÇÃO
                
                end.append(timer()) # End Time for Evaluation
        else:
            print('Please enter [ 0 ] - tf-idf ranking OR [ 1 ] - BM25 ranking!')
            sys.exit()
        return queries, scores, start, end
    
    
    
    #PUT IN MAIN
    #queries, scores, start, end = QueryProcess.getScores("queries.txt", rankType) """