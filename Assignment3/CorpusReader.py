#  Corpus reader that iterates over the collection (corpus) of a document and returns, in turn, the contents of each
#  document.
#
#  For this assignment it's only used the title and abstract fields and documents with an empty abstract are ignored.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070
import re
import timeit

class CorpusReader:

    def __init__(self, csvFName):
        self.csvFName = csvFName
        self.csv_file = None

    def startReadingCorpus(self):
        self.csv_file = open(self.csvFName, "r")
        self.csv_file.readline() # skip header

    def readDoc(self):
        #start = timeit.default_timer()

        line = self.csv_file.readline()

        if not line:
            self.csv_file.close()

            #stop = timeit.default_timer()
            print('Read last document from corpus reader')
            return -1

        # https://stackoverflow.com/questions/18893390/splitting-on-comma-outside-quotes
        line = re.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", line)   # any characters that are not a comma
        title = line[3]
        abstract = line[8]
        doi = line[0]
        if abstract is not None and abstract != '' and title is not None and title != '' and doi is not None and doi != '':
            #stop = timeit.default_timer()
            #print('readDoc: {} seconds'.format(stop - start))
            return doi, title, abstract

        #stop = timeit.default_timer()
        #print('readDoc: {} seconds'.format(stop - start))
        return None