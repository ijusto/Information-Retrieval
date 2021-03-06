# Main program.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import getopt
import sys
from os import path
import Evaluation
from Indexer import *
from Ranker import *
import Searcher
from timeit import default_timer as timer


def main(argv):
    collectionFile = ''
    tokenizerType = ''
    queriesFile = ''
    rankType = ''
    start = []
    end = []
    try:
        opts, args = getopt.getopt(argv, "hf:t:q:r:", ["collectionFile=", "tokenizerType=", "queriesFilePath=",
                                                     "rankType="])
    except getopt.GetoptError:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> '
              '-r <rankType: 0 - TF-IDF, 1 - BM25>')
        sys.exit()

    if len(opts) != 4:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> '
              '-r <rankType: 0 - TF-IDF, 1 - BM25>')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> '
                  '-r <rankType: 0 - TF-IDF, 1 - BM25>')
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
    (Indexer(collectionFile, tokenizerType)).writeIndexToFile('index')

    f = open(queriesFile, 'r')
    queries = f.read().splitlines()
    f.close()

    scores = []

    if tokenizerType == '0':  # simple
        tokenizer = Tokenizer.SimpleTokenizer('')
    else:  # better
        tokenizer = Tokenizer.BetterTokenizer('')

    for query in queries:

        # Query Operations
        tokenizer.changeText(query)
        queryTerms = tokenizer.getTerms()

        
        # Searcher
        documentsInfo, avgDocLen = Searcher.searchDocuments(queryTerms, 'index')

        # Ranker
        ranker = Ranker(documentsInfo, avgDocLen)
        
        # Start time (latency purpose)
        start.append(timer())
        # If rankType = 0 (tf-idf)
        if rankType == '0':
            scores += [ranker.lnc_ltc()]
        # If rankType = 1 (BM25)
        else:
            scores += [ranker.bm25(1.2, 0.75)]

        # End time (latency purpose)
        end.append(timer())

    # Evaluation
    Evaluation.getResults('./data/queries.relevance.txt', queries, scores, start, end)


if __name__ == "__main__":
    main(sys.argv[1:])
