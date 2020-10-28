# 1. Create a corpus reader that iterates over the collection (corpus) of document and returns, in turn, the contents of
# each document.
# For this assignment consider only the title and abstract fields and ignore documents with an empty abstract.

import numpy as np
import csv

class CorpusReader:

    def __init__(self, csv):
        self.csv = csv

    def readCorpus(self):
        with open(self.csv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            rows = list(csv_reader)
            corpus = [(rows[iter][0], rows[iter][2], rows[iter][7]) for iter in range(len(rows))
                             if rows[iter][7] is not None and rows[iter][7] != '' and rows[iter][0] != '']

        return corpus

cr = CorpusReader("data/all_sources_metadata_2020-03-13.csv")
print(cr.readCorpus())