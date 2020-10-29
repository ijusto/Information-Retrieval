## @package pyexample
#  Documentation for this module.
#
#  More details.

import CorpusReader
import Tokenizer
import timeit


## Documentation for a class.
#
#  More details.


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

        #   a) What was the total indexing time and how much memory (roughly) is required to index this collection?
        print('Indexing time - {} tokenizer: {}'.format("simple" if self.tokenizerType == "0" else "better",
                                                        stop - start))

        # NOT SURE (Review)
        # print('Memory required - {} tokenizer: {}'.format(self.col.memory_usage(index=True).sum(), self.tokenizerType))

        #   b) What is your vocabulary size?
        print('Vocabulary Size: {}'.format(len(self.term_map.keys())))

    ## Documentation for a method.
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

    ## Documentation for a method.
    #  @param self The object pointer.
    #   c) List the ten first terms (in alphabetic order) that appear in only one document (document frequency = 1).
    def getTermsInOneDoc(self):
        terms_sorted = sorted(self.term_map.keys())
        results = [term for term in terms_sorted if len(self.term_map[term].keys()) == 1]
        print('Ten first Terms in only 1 document: {}'.format(results[:10]))

    ## Documentation for a method.
    #  @param self The object pointer.
    #   d) List the ten terms with highest document frequency.
    def getHighestDocFreqTerms(self):
        doc_freq = sorted(self.term_map.keys(), key=lambda x: len(self.term_map[x].keys()))
        print('Ten terms with highest document frequency: {}'.format(doc_freq[:10]))
