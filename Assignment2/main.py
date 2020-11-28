# Main program.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import getopt
import sys
from os import path

from Indexer import Indexer
from QueryOperations import QueryOperations
from Ranker import Ranker
from Searcher import Searcher
from timeit import default_timer as timer


def main(argv):
    collectionFile = ''
    tokenizerType = ''
    queriesFile = ''
    rankType = ''
    start = []
    end = []
    try:
        opts, args = getopt.getopt(argv, "hf:t:q:", ["collectionFile=", "tokenizerType=", "queriesFilePath=", "rankType="])
    except getopt.GetoptError:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> -r <rankType: 0 - TF-IDF, 1 - BM25>')
        sys.exit()

    if len(opts) != 4:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> -r <rankType: 0 - TF-IDF, 1 - BM25>')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> -r <rankType: 0 - TF-IDF, 1 - BM25>')
            sys.exit()
        elif opt in ("-f", "--collectionFile"):
            if not path.exists(arg):
                print('Incorrect path to collection file.')
                sys.exit()
            collectionFile = arg
        elif opt in ("-t", "--tokenizerType"):
            if arg != '0' and arg != '1':
                print('Incorrect tokenizer type. Simple tokenizer: 0, Better tokenizer: 1.')
                sys.exit()
            tokenizerType = arg
        elif opt in ("-q", "--queriesFilePath"):
            if not path.exists(arg):
                print('Incorrect path to queries file.')
                sys.exit()
            queriesFile = arg
        elif opt in ("-r", "--rankType"):
            if arg != '0' and arg != '1':
                print('Incorrect rank type. TF-IDF: 0, BM25: 1.')
                sys.exit()
            rankType = arg

    # Indexer
    indexer = Indexer(collectionFile, tokenizerType)
    indexer.writeIndexToFile('index')

    f = open(queriesFile, 'r')
    queries = f.readlines()
    f.close()

    for query in queries:
        start.append(timer())
        # Query operations
        queriesTerms = QueryOperations(tokenizerType, query).getQueriesTerms()

        # Searcher
        searcher = Searcher(queriesTerms)

        #Ranker
        ranker = Ranker(searcher.searchDocuments('index'))
        
        # If rankType = 0 (tf-idf)
        if rankType == '0':
            _ = ranker.lnc_ltc()
                
        # If rankType = 1 (BM25)
        else:
            # lenD is the length of the document D in words
            # avgdl is the average document length in the text collection from which documents are drawn
            _ = ranker.bm25(lenD, avgdl, 1.2, 0.75)

            
        end.append(timer())


if __name__ == "__main__":
    main(sys.argv[1:])
