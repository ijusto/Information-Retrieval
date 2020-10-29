# 3. Create an indexing pipeline. Use a suitable data structure for the index, defined by you.

# 4. Index the corpus using each tokenizer above and answer the following questions:
#   a) What was the total indexing time and how much memory (roughly) is required to index this collection?
#   b) What is your vocabulary size?
#   c) List the ten first terms (in alphabetic order) that appear in only one document (document frequency = 1).
#   d) List the ten terms with highest document frequency.
import CorpusReader
import Tokenizer
import timeit

class Indexer:

    def __init__(self, collection, tokenizerType):
        self.col = CorpusReader.CorpusReader(collection).readCorpus() # list((doi, title, abstract))
        self.token_map = {}  # key: token, value: doc_freq_map
        self.vocab_size = 0
        self.tokenizerType = tokenizerType

    def index(self):
        for doi, title, abstract in self.col:
            if self.tokenizerType == 0: # simple
                tokenizer = Tokenizer.SimpleTokenizer(title, abstract)
            else: # better
                tokenizer = Tokenizer.BetterTokenizer(title, abstract)

            terms = tokenizer.getTerms()
            start = timeit.default_timer()
            for term in terms:
                if term in self.token_map.keys():
                    if doi in self.token_map[term].keys():
                        self.token_map[term][doi] += 1
                    else:
                        self.token_map[term][doi] = 1
                else:
                    token_freq_map = {}  # key: docId, value: token_freq
                    token_freq_map[doi] = 1
                    self.token_map[term] = token_freq_map[doi]
            stop = timeit.default_timer()

            #   a) What was the total indexing time and how much memory (roughly) is required to index this collection?
            print('Indexing time - {} tokenizer: {}').format(self.tokenizerType, stop - start)
            
            # NOT SURE (Review)
            print('Memory required - {} tokenizer: {}').format(self.tokenizerType, self.col.memory_usage(index=True).sum()) 

            #   b) What is your vocabulary size?simple
            self.vocab_size = len(self.token_map.keys())

    #   c) List the ten first terms (in alphabetic order) that appear in only one document (document frequency = 1).
    def getTermsInOneDoc(self):
        terms_sorted = sorted(self.token_map.keys())

        simple_results = [term for term in terms_sorted if len(self.token_map[term].keys() == 1)]
        print('Ten first Terms : {}').format(simple_results[:10])

    #   d) List the ten terms with highest document frequency.
    def getHighestDocFreqTerms(self):

        doc_freq = sorted(self.token_map.keys(), key=lambda x: len(self.token_map[x].keys()))
        print('Ten terms with highest document frequency: {}').format(doc_freq[:10])


