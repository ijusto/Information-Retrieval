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

# Single-pass in-memory Indexer
class Indexer:

    # The constructor.
    #  @param self The object pointer.
    #  @param collectionPath The path to the csv containing the collection
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, collectionPath, tokenizerType):
        self.tokenizerType = tokenizerType
        self.collectionPath = collectionPath

        # dictionary of dictionaries {term: {docId: term_logWeight}} - for each term postings with term_logWeight
        # (length = number of terms)
        self.postingsMaps = {}

        # total number of documents in the collection
        self.N = 0

    #  todo: description
    #  @param self The object pointer.
    def index(self, withPositions=False):

        self.N = 0

        if self.tokenizerType == '0':  # simple
            tokenizer = Tokenizer.SimpleTokenizer('')
        else:  # better
            tokenizer = Tokenizer.BetterTokenizer('')

        # percentage of available memory system-wide
        #psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

        pid = os.getpid()

        # memory used by the current Python instance
        #memoryUse = psutil.Process(os.getpid()).memory_info()[0] / 2. ** 30  # memory use in GB...I think

        #print('memory use:', psutil.Process(os.getpid()).memory_info()[0] / 2. ** 30, ", available memory: ",
        #      psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)

        memoryUsePercLimit = psutil.Process(os.getpid()).memory_percent()*100 + 10
        for doi, title, abstract in CorpusReader.CorpusReader(self.collectionPath).readCorpus():
            self.N += 1
            tokenizer.changeText(title + " " + abstract)
            terms = tokenizer.getTerms(withPositions=withPositions) # todo: check if terms is a dict or a list ...

            # first, we populate the dictionary postingsMaps with the term frequency {term: {docId: term_freq} }
            nDicts = 0
            for term in terms:
                if psutil.Process(os.getpid()).memory_percent()*100 >= memoryUsePercLimit:
                    self.writeIndexToFile('dict' + str(nDicts))
                    nDicts += 1
                    # todo: clean postingsMaps

                if term in self.postingsMaps.keys():
                    if doi in self.postingsMaps[term].keys():
                        self.postingsMaps[term][doi] += 1
                    else:
                        self.postingsMaps[term][doi] = 1
                else:
                    self.postingsMaps[term] = {doi: 1}  # key: docId, value: term_freq

        # lnc (logarithmic term frequency, no document frequency, cosine normalization)
        # then, we modify the postingsMaps from {term: {docId: term_freq}} to {term: idf, {docId: weight}}
        # logarithmic term frequency
        self.postingsMaps = {term: (getIDFt(term, self.postingsMaps, self.N),
                                    {docId: getLogWeight(term, docId, self.postingsMaps)
                                    for docId in self.postingsMaps[term].keys()})
                             for term in self.postingsMaps.keys()}

        # order by term_idf and then by term_weight (both reversed)
        # Postings of low-idf terms have many docs
        #self.postingsMaps = dict(sorted({t: (idf, dict(sorted({doid: w for doid, w in pMap.items()}.items(),
        #                                                      key=lambda items: items[1], reverse=True)))
        #                                 for t, (idf, pMap) in self.postingsMaps.items()}.items(),
        #                                key=lambda items: self.postingsMaps[items[0]][0], reverse=True))

    # 2. Write the resulting index to file using the following format (one term per line):
    #       term:id|doc_id:term_weight:pos1,pos2,pos3,...|doc_id:term_weight:pos1,pos2,pos3,...
    # todo: change this
    def writeIndexToFile(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

        indexFile = open(filename, 'w')

        indexFile.writelines([term + ':' + str(idf) + '|' + ''.join([str(doc_id) + ':' + str(term_weight) + '|'
                                                                     for doc_id, term_weight in pMap.items()]) + '\n'
                              for term, (idf, pMap) in self.postingsMaps.items()])

        indexFile.close()

    # todo: description
    def getVocabularySize(self):
        return len(self.postingsMaps)