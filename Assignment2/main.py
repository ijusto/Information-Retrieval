# Main program.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import getopt
import sys
from os import path

from Indexer import Indexer
from QueryOperations import QueryOperations
from Searcher import Searcher


def main(argv):
    collectionFile = ''
    tokenizerType = ''
    queriesFile = ''
    try:
        opts, args = getopt.getopt(argv, "hf:t:q:", ["collectionFile=", "tokenizerType=", "queriesFilePath="])
    except getopt.GetoptError:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath>')
        sys.exit()

    if len(opts) != 3:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath>')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better>')
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

    # Indexer
    indexer = Indexer(collectionFile, tokenizerType)
    indexer.writeIndexToFile('index')

    # Query operations
    queryOperations = QueryOperations(tokenizerType, queriesFile)
    queryOperations.readQueries()
    queriesTerms = queryOperations.getQueriesTerms()

    # Searcher
    searcher = Searcher(queriesTerms)
    searcher.getQueryScoresFromIndexer('index')


if __name__ == "__main__":
    main(sys.argv[1:])
