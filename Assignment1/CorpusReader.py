# 1. Create a corpus reader that iterates over the collection (corpus) of document and returns, in turn, the contents of
# each document.
# For this assignment consider only the title and abstract fields and ignore documents with an empty abstract.

import numpy as np
import csv

class CorpusReader:

    def __init__(self, csv):
        self.csv = csv

    def readCorpus(self):
        corpus = []
        with open(self.csv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            rows = list(csv_reader)
            # doi, title, abstract
            for iter in range(len(rows)):
                doi = rows[iter][3].replace("doi.org/", "").replace("http://dx.doi.org/", "")
                title = rows[iter][2]
                abstract = rows[iter][7]
                if doi.startswith("10.") and abstract is not None and abstract != '' and title is not None and title != '':
                    corpus += [(doi, title, abstract)]

        return corpus

cr = CorpusReader("data/all_sources_metadata_2020-03-13.csv")
#print(cr.readCorpus())