from Indexer import Indexer
from os import path
import sys, getopt

def main(argv):
    collectionFile = ''
    tokenizerType = ''
    try:
        opts, args = getopt.getopt(argv,"hf:t:",["collectionFile=","tokenizerType="])
    except getopt.GetoptError:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better>')
        sys.exit()

    if len(opts) != 2:
        print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better>')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better>')
            sys.exit()
        elif opt in ("-f", "--collectionFile"):
            if not path.exists(arg):
                print('Incorrect path to collection file.')
                sys.exit()
            elif not path.exists(arg):
                print('File doesn\'t exists')
                sys.exit()
            collectionFile = arg
        elif opt in ("-t", "--tokenizerType"):
            if arg != '0' and arg != '1':
                print('Incorrect tokenizer type. Simple tokenizer: 0, Better tokenizer: 1.')
                sys.exit()
            tokenizerType = arg

    print('before')
    indexer = Indexer(collectionFile, tokenizerType)
    indexer.index()
    print('after')
    indexer.getTermsInOneDoc()
    print('after')
    indexer.getHighestDocFreqTerms()
    print('after')

if __name__ == "__main__":
   main(sys.argv[1:])