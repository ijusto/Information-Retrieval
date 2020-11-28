# Indexer.
#  Constructs an inverted index of word (term) to document pointers.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import CorpusReader
import Tokenizer
import timeit
import psutil
import os
from ScoreCalculations import *


# Indexer
class Indexer:

    # The constructor.
    #  @param self The object pointer.
    #  @param collectionPath The path to the csv containing the collection
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, collectionPath, tokenizerType):
        start = timeit.default_timer()
        self.tokenizerType = tokenizerType
        self.collectionPath = collectionPath

        # dictionary of dictionaries {term: {docId: term_logWeight}} - for each term postings with term_logWeight
        # (length = number of terms)
        self.postingsMaps = {}

        # total number of documents in the collection
        self.N = 0

        self.index()
        stop = timeit.default_timer()

        #   a) What was the total indexing time?
        print('Indexing time - {} tokenizer: {} seconds'.format("simple" if self.tokenizerType == "0" else "better",
                                                                stop - start))

        # How much memory (roughly) is required to index this collection?
        process = psutil.Process(os.getpid())
        print('\nMemory required for indexing: {} MB'.format(process.memory_info().rss / 1000000))  # rss in bytes

        #   b) What is your vocabulary size?
        print('\nVocabulary Size: {}'.format(len(self.postingsMaps)))

    #  todo: description
    #  @param self The object pointer.
    def index(self):

        collection = CorpusReader.CorpusReader(self.collectionPath).readCorpus()  # list((doi, title, abstract))
        self.N = len(collection)

        for doi, title, abstract in CorpusReader.CorpusReader(self.collectionPath).readCorpus():
            if self.tokenizerType == '0':  # simple
                tokenizer = Tokenizer.SimpleTokenizer(title + " " + abstract)
            else:  # better
                tokenizer = Tokenizer.BetterTokenizer(title + " " + abstract)

            terms = tokenizer.getTerms()

            # first, we populate the dictionary postingsMaps with the term frequency {term: {docId: term_freq} }
            for term in terms:
                if term in self.postingsMaps.keys():
                    if doi in self.postingsMaps[term].keys():
                        self.postingsMaps[term][doi] += 1
                    else:
                        self.postingsMaps[term][doi] = 1
                else:
                    self.postingsMaps[term] = {doi: 1}  # key: docId, value: term_freq

        # lnc (logarithmic term frequency, no document frequency, cosine normalization)
        # then, we modify the postingsMaps from {term: {docId: term_freq}} to {term: {docId: weight}}
        # logarithmic term frequency
        self.postingsMaps = {term: {docId: getLogWeight(term, docId, self.postingsMaps)
                                    for docId in self.postingsMaps[term].keys()}
                             for term in self.postingsMaps.keys()}

        # order by term_idf and then by term_weight (both reversed)
        # Postings of low-idf terms have many docs
        self.postingsMaps = dict(sorted({t: (idf, dict(sorted({doid: w for doid, w in pMap.items()}.items(),
                                                              key=lambda items: items[1], reverse=True)))
                                         for t, (idf, pMap) in self.postingsMaps.items()}.items(),
                                        key=lambda items: self.postingsMaps[items[0]][0], reverse=True))

    # 1.3. Add a method to write the resulting index to file. Use the following format, or a similar one (one term per
    #       line): term:idf;doc_id:term_weight;doc_id:term_weight;...
    def writeIndexToFile(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

        indexFile = open(filename, 'w')

        indexFile.writelines([term + ':' + str(idf) + ';' + ''.join([str(doc_id) + ':' + str(term_weight) + ';'
                                                                     for doc_id, term_weight in pMap.items()]) + '\n'
                              for term, (idf, pMap) in self.postingsMaps.items()])

        indexFile.close()
