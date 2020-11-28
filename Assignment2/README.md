# Assignment 2
Weighted (tf-idf) indexer and a ranked retrieval method.

Usage
----------------------
    main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better> -q <queriesFilePath> -r <rankType: 0 - TF-IDF, 1 - BM25>
    
Example:

    python3 main.py -f ./data/all_sources_metadata_2020-03-13.csv -t 1 -q ./data/queries.txt -r 0


    



