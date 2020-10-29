# Assignment 1
Simple document indexer, consisting of a corpus reader /
document processor, tokenizer, and indexer.

Usage
----------------------

    main.py -f <collectionFile> -t <tokenizerType: 0 - Simple, 1 - Better>
    
Example:

    python3 main.py -f ./data/all_sources_metadata_2020-03-13.csv -t 1



[PyStemmer]("https://github.com/snowballstem/pystemmer") Installation
----------------------
PyStemmer (<https://github.com/snowballstem/pystemmer>) uses distutils, so all that is necessary to build and install
PyStemmer is the usual distutils invocation:

    python setup.py install

You can also install using ``pip``:

    * from PyPI: ``pip install pystemmer``
    * from a local copy of the code: ``pip install .``
    * from git: ``pip install git+git://github.com/snowballstem/pystemmer``

