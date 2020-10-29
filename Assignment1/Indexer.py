## @package pyexample
#  Documentation for this module.
#
#  More details.

import CorpusReader
import Tokenizer
import timeit
import psutil
import os


## Indexer
class Indexer:

    ## The constructor.
    #  @param self The object pointer.
    #  @param collection The path to the csv containing the collection
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, collection, tokenizerType):
        start = timeit.default_timer()
        self.col = CorpusReader.CorpusReader(collection).readCorpus()  # list((doi, title, abstract))
        self.term_map = {}  # key: term, value: doc_freq_map (key: doi, value: term_freq)
        self.tokenizerType = tokenizerType
        self.index()
        stop = timeit.default_timer()

        #   a) What was the total indexing time?
        print('Indexing time - {} tokenizer: {}'.format("simple" if self.tokenizerType == "0" else "better",
                                                        stop - start))

        # How much memory (roughly) is required to index this collection?
        process = psutil.Process(os.getpid())
        print(process.memory_info().wset/1024**2)
        print(process.memory_info().peak_wset/1024**2)

        #   b) What is your vocabulary size?
        print('\nVocabulary Size: {}'.format(len(self.term_map.keys())))

    ## Populates the term_map dictionary with another dictionary with doi's as keys and the term's frequency in that document
    #  @param self The object pointer.
    def index(self):
        for doi, title, abstract in self.col:
            if self.tokenizerType == '0':  # simple
                tokenizer = Tokenizer.SimpleTokenizer(title, abstract)
            else:  # better
                tokenizer = Tokenizer.BetterTokenizer(title, abstract)

            terms = tokenizer.getTerms()
            for term in terms:
                if term in self.term_map.keys():
                    if doi in self.term_map[term].keys():
                        self.term_map[term][doi] += 1
                    else:
                        self.term_map[term][doi] = 1
                else:
                    term_freq_map = {}  # key: docId, value: term_freq
                    term_freq_map[doi] = 1
                    self.term_map[term] = term_freq_map

    ## Lists the ten first terms (in alphabetic order) that appear in only one document (document frequency = 1).
    #  @param self The object pointer.
    def listTermsInOneDoc(self):
        terms_sorted = sorted(self.term_map.keys())
        results = [term for term in terms_sorted if len(self.term_map[term].keys()) == 1]
        print('Ten first Terms in only 1 document: {}'.format(results[:10]))

    ## Lists the ten terms with highest document frequency.
    #  @param self The object pointer.
    def listHighestDocFreqTerms(self):
        doc_freq = sorted(self.term_map.keys(), key=lambda x: len(self.term_map[x].keys()))
        print('Ten terms with highest document frequency: {}'.format(doc_freq[:10]))
