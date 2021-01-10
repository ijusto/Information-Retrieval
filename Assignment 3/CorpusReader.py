#  Corpus reader that iterates over the collection (corpus) of a document and returns, in turn, the contents of each
#  document.
#
#  For this assignment it's only used the title and abstract fields and documents with an empty abstract are ignored.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

class CorpusReader:

    def __init__(self, csvFName):
        self.csvFName = csvFName
        self.csv_file = None

    def startReadingCorpus(self):
        self.csv_file = open(self.csvFName, "r")
        self.csv_file.readline() # skip header

    def readDoc(self):
        line = self.csv_file.readline()

        if not line:
            self.csv_file.close()
            return -1

        # https://stackoverflow.com/questions/18893390/splitting-on-comma-outside-quotes
        line = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)")   # any characters that are not a comma
        print(line)
        title = line[3]
        abstract = line[10]
        doi = line[0]
        if abstract is not None and abstract != '' and title is not None and title != '' and doi is not None and doi != '':
            return doi, title, abstract

        return None