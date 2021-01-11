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

        memoryUsePercLimit = psutil.Process(os.getpid()).memory_percent()*100 + (psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)/2 # percentage of memory used by the current Python instance plus 10%
        print('start memory available: {}%'.format(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))

        corpusReader.startReadingCorpus()
        nDicts = 0

        if self.withPositions:

            while True:

                # -------------------------------------------- Get Document --------------------------------------------
                doc = corpusReader.readDoc()
                if doc == -1:
                    if self.postingsMaps != {}:
                        # start = timeit.default_timer()
                        self.writeIndexToFileWithPositions('./dicts/dict' + str(nDicts))
                        # stop = timeit.default_timer()
                        # print('write: {} seconds'.format(stop - start))
                        # print('memory used: {} %'.format(psutil.Process(os.getpid()).memory_percent() * 100))
                        print('available memory: {} %'.format(
                            psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))

                        nDicts += 1
                        self.postingsMaps = {}  # clean dictionary
                    break
                elif doc == None:
                    continue

                (doi, title, abstract) = doc
                del doc
                self.N += 1
                #startdocreadtime = timeit.default_timer()

                # ------------------------------------------- Get Document Terms ---------------------------------------
                tokenizer.changeText(title + " " + abstract)
                del title
                del abstract
                terms, termPositions = tokenizer.getTerms(withPositions=self.withPositions)
                tokenizer.changeText("")  # clean term memory from tokenizer

                # first, we populate the dictionary postingsMaps with the term frequency {term: {docId: [termpositions]} }

                if (psutil.virtual_memory().available * 100 / psutil.virtual_memory().total) <= 10 and self.postingsMaps != {}:  # available memory
                    #start = timeit.default_timer()
                    self.writeIndexToFileWithPositions('./dicts/dict' + str(nDicts))
                    #stop = timeit.default_timer()
                    #print('write: {} seconds'.format(stop - start))
                    #print('memory used: {} %'.format(psutil.Process(os.getpid()).memory_percent() * 100))
                    print('available memory: {} %'.format(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))

                    nDicts += 1
                    self.postingsMaps = {}  # clean dictionary
                else:
                    #while terms != [] and termPositions != []:
                    #    if terms[0] in self.postingsMaps.keys():
                    #        #if doi not in self.postingsMaps[terms[0]].keys(): -> doi always not in self.postingsMaps[terms[0]].keys()
                    #        self.postingsMaps[terms[0]][doi] = termPositions[0]
                    #    else:
                    #        self.postingsMaps[terms[0]] = {doi: termPositions[0]}  # key: docId, value: [pos1,pos2,pos3,...]
                    #
                    #    terms = terms[1:]
                    #    termPositions = termPositions[1:]

                    _ = [self.postingsMaps.update({terms[termInd]: {doi: termPositions[termInd]}})
                                if terms[termInd] not in self.postingsMaps.keys()
                                else self.postingsMaps[terms[termInd]].update({doi: termPositions[termInd]})
                            for termInd in range(len(terms))]

                    del terms
                    del termPositions

                #enddocreadtime = timeit.default_timer()
                #print('document {}: {} seconds'.format(doi, enddocreadtime - startdocreadtime))

            # todo: merge dictionaries
            self.postingsMaps = {}

            start = timeit.default_timer()
            final_dict = open("index", "w")
            dict_names = ['./dicts/dict' + str(nDict) for nDict in range(nDicts)]
            if nDicts > 1:
                temp_dicts = [open(dict_name, "r") for dict_name in dict_names]
                while temp_dicts != []:
                    for dict_file in temp_dicts:
                        # ---------------------- Read first line of each file ------------------------------------------
                        line = dict_file.readline()

                        if not line:
                            dict_file.close()
                            # delete dictionary block from disk
                            os.remove(dict_names[temp_dicts.index(dict_file)])
                            dict_names.remove(dict_names[temp_dicts.index(dict_file)])
                            temp_dicts.remove(dict_file)
                            continue

                        # ------------------------ Save line info to memory --------------------------------------------
                        info = line.split('[:]+|[|]+') # 'term', 'docid', 'pos1,pos2,pos3', 'docid', 'pos1,pos2,pos3', ...
                        term = info[0] # term
                        docIds = info[1:][0::2] # [docid, docid, ...]
                        termPositions = [positions.split(',') for positions in info[1:][1::2]] # [[pos1,pos2,pos3], [pos1,pos2,pos3], ...]

                        if term in self.postingsMaps.keys():
                            #for docId in docIds:
                                # if docId in line_temp_dict[term].keys(): -> doesnt happpen because we only write to file after reading the hole document
                            # merge postings list (update in order if dict document)
                            self.postingsMaps[term].update({docIds[docInd]:termPositions[docInd] for docInd in range(len(docIds))})
                        else:
                            self.postingsMaps.update({term: {docIds[docInd]:termPositions[docInd] for docInd in range(len(docIds))}})

                    # todo: verify all this functions (storecalculations) work with this new self.postingsMaps dictionary structure
                    # get first element of alphabetical sorted list of terms in memory
                    minorTerm = sorted(self.postingsMaps.keys())[0]

                    # write its information to the final dictionary\
                    final_dict.writelines(
                        [minorTerm + ':' +                                                                 # term:
                         str(getIDFt(minorTerm, self.postingsMaps, self.N)) + ';' +                        # idf;
                         ''.join([str(doc_id) + ':' +                                                      # doc_id:
                                  str(getLogWeightPositions(minorTerm, doc_id, self.postingsMaps)) + ':' + # term_weight:
                                  ','.join([str(pos) for pos in positions]) + ';'                          # pos1,pos2,...
                                            for doc_id, positions in self.postingsMaps[minorTerm].items()]) + '\n'])

                    # remove it from memory
                    del self.postingsMaps[minorTerm]
                    del minorTerm


            else:
                temp_dict = open('./dicts/dict0', 'r')
                # todo: read line from temp_dict, calculate weights and write to final_dict


            stop = timeit.default_timer()
            print('merge and write of final dictionary: {} seconds'.format(stop - start))
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
                    if (psutil.virtual_memory().available * 100 / psutil.virtual_memory().total) <= 20: # available memory
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
    def writeIndexToFileWithPositions(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

        indexFile = open(filename, 'w')

        # sort postingsMaps by terms
        self.postingsMaps = dict(sorted(self.postingsMaps.items()))

        # term:docid:pos0,pos1,pos2|docid
        indexFile.writelines([term + ':' + ''.join([str(doc_id) + ':' + ','.join([str(pos) for pos in termPositions]) + '|'
                                                                     for doc_id, termPositions in pMap.items()]) + '\n'
                              for term, pMap in self.postingsMaps.items()])

        indexFile.close()

    # 2. Write the resulting index to file using the following format (one term per line):
    #       term:id|doc_id:term_weight:pos1,pos2,pos3,...|doc_id:term_weight:pos1,pos2,pos3,...
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