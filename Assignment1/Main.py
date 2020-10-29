from Indexer import Indexer

def main():
    print('before')
    simple_ind = Indexer("data/all_sources_metadata_2020-03-13.csv", 0).index()
    better_ind = Indexer("data/all_sources_metadata_2020-03-13.csv", 1).index()
    print('after')
    simple_ind.getTermsInOneDoc()
    better_ind.getTermsInOneDoc()
    print('after')
    simple_ind.getHighestDocFreqTerms()
    better_ind.getHighestDocFreqTerms()
    print('after')
main() 
        