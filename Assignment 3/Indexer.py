# Indexer.
#  Constructs an inverted index of word (term) to document pointers.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import CorpusReader
import Tokenizer
import timeit
import sys
import psutil
import os
from ScoreCalculations import *

# Single-pass in-memory Indexer
class Indexer:

    # The constructor.
    #  @param self The object pointer.
    #  @param collectionPath The path to the csv containing the collection
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, collectionPath, tokenizerType, withPositions):
        self.tokenizerType = tokenizerType
        self.collectionPath = collectionPath
        self.withPositions = withPositions

        # dictionary of dictionaries {term: {docId: term_logWeight}} - for each term postings with term_logWeight
        # (length = number of terms)
        self.postingsMaps = {}

        # total number of documents in the collection
        self.N = 0

    #  todo: description
    #  @param self The object pointer.
    def index(self):

        self.N = 0

        if self.tokenizerType == '0':  # simple
            tokenizer = Tokenizer.SimpleTokenizer('')
        else:  # better
            tokenizer = Tokenizer.BetterTokenizer('')

        corpusReader = CorpusReader.CorpusReader(self.collectionPath)

        memoryUsePercLimit = psutil.Process(os.getpid()).memory_percent()*100 + 10 # percentage of memory used by the current Python instance plus 10%

        corpusReader.startReadingCorpus()

        if self.withPositions:

            while True:

                # -------------------------------------------- Get Document --------------------------------------------
                doc = corpusReader.readDoc()
                if doc == -1:
                    break
                elif doc == None:
                    continue

                (doi, title, abstract) = doc

                self.N += 1


                # ------------------------------------------- Get Document Terms ---------------------------------------
                tokenizer.changeText(title + " " + abstract)
                terms, termPositions = tokenizer.getTerms(withPositions=self.withPositions)

                # first, we populate the dictionary postingsMaps with the term frequency {term: {docId: [termpositions]} }
                nDicts = 0

                for termInd in range(len(terms)):
                    #if psutil.Process(os.getpid()).memory_percent() * 100 >= memoryUsePercLimit:
                    if (psutil.virtual_memory().available * 100 / psutil.virtual_memory().total) <= 10: # available memory

                        start = timeit.default_timer()
                        self.writeIndexToFile('./dicts/dict' + str(nDicts))
                        stop = timeit.default_timer()
                        print('write: {} seconds'.format( stop - start))

                        nDicts += 1
                        self.postingsMaps = {}  # clean dictionary

                    if terms[termInd] in self.postingsMaps.keys():
                        if doi not in self.postingsMaps[terms[termInd]].keys():
                            self.postingsMaps[terms[termInd]][doi] = termPositions[termInd]
                    else:
                        self.postingsMaps[terms[termInd]] = {doi: termPositions[termInd]}  # key: docId, value: [pos1,pos2,pos3,...]

                # todo: merge dictionaries
                # todo: weights (term freq = len(postitions)

        else:
            while True:
                doc = corpusReader.readDoc()
                if doc == -1:
                    break
                elif doc == None:
                    continue

                (doi, title, abstract) = doc

                self.N += 1
                tokenizer.changeText(title + " " + abstract)
                terms = tokenizer.getTerms(withPositions=self.withPositions)

                # first, we populate the dictionary postingsMaps with the term frequency {term: {docId: term_freq} }
                nDicts = 0

                for term in terms:
                    #if psutil.Process(os.getpid()).memory_percent() * 100 >= memoryUsePercLimit:
                    if (psutil.virtual_memory().available * 100 / psutil.virtual_memory().total) <= 10: # available memory
                        # lnc (logarithmic term frequency, no document frequency, cosine normalization)
                        # then, we modify the postingsMaps from {term: {docId: term_freq}} to {term: idf, {docId: weight}}
                        # logarithmic term frequency
                        self.postingsMaps = {term: (getIDFt(term, self.postingsMaps, self.N),
                                                    {docId: getLogWeight(term, docId, self.postingsMaps)
                                                     for docId in self.postingsMaps[term].keys()})
                                             for term in self.postingsMaps.keys()}
                        self.writeIndexToFile('./dicts/dict' + str(nDicts))
                        nDicts += 1
                        self.postingsMaps = {}  # clean dictionary

                    if term in self.postingsMaps.keys():
                        if doi in self.postingsMaps[term].keys():
                            self.postingsMaps[term][doi] += 1
                        else:
                            self.postingsMaps[term][doi] = 1
                    else:
                        self.postingsMaps[term] = {doi: 1}  # key: docId, value: term_freq

                # todo: merge dictionaries


    # 2. Write the resulting index to file using the following format (one term per line):
    #       term:id|doc_id:term_weight:pos1,pos2,pos3,...|doc_id:term_weight:pos1,pos2,pos3,...
    def writeIndexToFile(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

        indexFile = open(filename, 'w')

        if self.withPositions:
            indexFile.writelines([term + ':' + ''.join([str(doc_id) + ':' + ','.join([str(pos) for pos in termPositions])
                                                                         for doc_id, termPositions in pMap.items()]) + '\n'
                                  for term, pMap in self.postingsMaps.items()])
        else:
            indexFile.writelines([term + ':' + str(idf) + '|' + ''.join([str(doc_id) + ':' + str(term_weight) + '|'
                                                                         for doc_id, term_weight in pMap.items()]) + '\n'
                                  for term, (idf, pMap) in self.postingsMaps.items()])

        indexFile.close()

    # todo: description
    def getVocabularySize(self):
        return len(self.postingsMaps)