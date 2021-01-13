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

    # ----------------------------------------- HANDLING PROGRAM INPUT -------------------------------------------------
    collectionFile = ''
    tokenizerType = ''
    queriesFile = ''
    rankType = ''
    storePos = ''
    proximity = ''
    try:
        opts, args = getopt.getopt(argv, "hf:t:q:r:p:b", ["collectionFile=", "tokenizerType=", "queriesFilePath=",
                                                     "rankType=", "storePositions=", "proximityBoost="])
    except getopt.GetoptError:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> '
              '-r <rankType: 0 - TF-IDF, 1 - BM25> -p <storePositions: 0 - No, 1 - Yes '
              '-b <proximityBoost: 0 - No, 1 - Yes')
        sys.exit()

    if len(opts) != 6:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> '
              '-r <rankType: 0 - TF-IDF, 1 - BM25> -p <storePositions: 0 - No, 1 - Yes '
              '-b <proximityBoost: 0 - No, 1 - Yes')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> '
                  '-r <rankType: 0 - TF-IDF, 1 - BM25> -p <storePositions: 0 - No, 1 - Yes '
              '-b <proximityBoost: 0 - No, 1 - Yes')
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
        elif opt in ("-p", "--storePositions"):
            if arg != '0' and arg != '1':
                print('\nIncorrect store positions choice. No: 0, Yes: 1.')
                sys.exit()
            storePos = arg
        elif opt in ("-b", "--proximityBoost"):
            if arg != '0' and arg != '1':
                print('\nIncorrect proximity boost choice. No: 0, Yes: 1.')
                sys.exit()
            proximity = arg

    # ----------------------------------------------- INDEXER ----------------------------------------------------------
    indexer = Indexer(collectionFile, tokenizerType, True if storePos=='1' else False)

    start = timeit.default_timer()
    indexer.index()
    stop = timeit.default_timer()

    #   a) What was the total indexing time?
    print('Indexing time - {} tokenizer: {} min and {} seconds'.format("simple" if tokenizerType == "0" else "better", (stop - start)//60, (stop - start) % 60))

    # How much memory (roughly) is required to index this collection?
    process = psutil.Process(os.getpid())
    print('\nMemory required for indexing: {} MB'.format(process.memory_info().rss / 1000000))  # rss in bytes

    #   b) What is your vocabulary size?
    print('\nVocabulary Size: {}'.format(indexer.getVocabularySize()))

    f = open(queriesFile, 'r')
    queries = f.read().splitlines()
    f.close()

    scores = []

    if tokenizerType == '0':  # simple
        tokenizer = Tokenizer.SimpleTokenizer('')
    else:  # better
        tokenizer = Tokenizer.BetterTokenizer('')

    start = []
    end = []
    for query in queries:

        # --------------------------------------- QUERY OPERATIONS -----------------------------------------------------
        tokenizer.changeText(query)

        queryTerms, queryTermsPositions = tokenizer.getTerms(withPositions=True if storePos == '1' else False)


        # ------------------------------------------- SEARCHER ---------------------------------------------------------
        documentsInfo, avgDocLen = Searcher.searchDocuments(queryTerms, 'index', True if storePos == '1' else False)

        # -------------------------------------------- RANKER ----------------------------------------------------------
        ranker = Ranker(documentsInfo, avgDocLen)
        
        # Start time (latency purpose)
        start.append(timer())
        # If rankType = 0 (tf-idf)
        if rankType == '0':
            # If proximity = 1 (Proximity Boost)
            if proximity == '1':
                scores += [ranker.proximity_boost(ranker.lnc_ltc(), queryTerms)]
            else:
                scores += [ranker.lnc_ltc()]
        # If rankType = 1 (BM25)
        else:
            # If proximity = 1 (Proximity Boost)
            if proximity == '1':
                scores += [ranker.proximity_boost(ranker.bm25(1.2, 0.75), queryTerms)]
            else:
                scores += [ranker.bm25(1.2, 0.75)]

        # End time (latency purpose)
        end.append(timer())

    # Evaluation
    Evaluation.getResults('./data/queries.relevance.txt', queries, scores, start, end)


if __name__ == "__main__":
    main(sys.argv[1:])
