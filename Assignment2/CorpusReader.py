#  Corpus reader that iterates over the collection (corpus) of a document and returns, in turn, the contents of each
#  document.
#
#  For this assignment it's only used the title and abstract fields and documents with an empty abstract are ignored.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070


import csv


class CorpusReader:

    def __init__(self, csvFName):
        self.csvFName = csvFName

    def readCorpus(self) -> list:
        corpus = []
        with open(self.csvFName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            rows = list(csv_reader)
            # doi, title, abstract
            for iRow in range(len(rows)):
                doi = rows[iRow][3].replace("doi.org/", "").replace("http://dx.doi.org/", "")
                title = rows[iRow][2]
                abstract = rows[iRow][7]
                if doi.startswith("10.") and abstract is not None and abstract != '' and title is not None\
                        and title != '':
                    corpus += [(doi, title, abstract)]

        return corpus
