# 1. Create a corpus reader that iterates over the collection (corpus) of document and returns, in turn, the contents of
# each document.
# For this assignment consider only the title and abstract fields and ignore documents with an empty abstract.

import pandas as pd
import numpy as np

class CorpusReader:

    def __init__(self, csv):
        self.csv = csv

    def readCorpus(self):
        data = pd.read_csv(self.csv)
        corpus = list(zip(data['sha'], data['title'], data['abstract']))
        clean_collection = [(sha, title, abst) for (sha, title, abst) in corpus if abst is not np.nan]
        return clean_collection