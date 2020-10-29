from Indexer import Indexer

def main():
    print('before')
    ind = Indexer("data/all_sources_metadata_2020-03-13.csv", 0).index()
    print('after')
    tenOne = Indexer("data/all_sources_metadata_2020-03-13.csv", 0).getTermsInOneDoc()
    print('after')
    tenHigh = Indexer("data/all_sources_metadata_2020-03-13.csv", 0).getHighestDocFreqTerms()
    print('after')
main() 
        