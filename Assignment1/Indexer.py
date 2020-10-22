# 3. Create an indexing pipeline. Use a suitable data structure for the index, defined by you.

# 4. Index the corpus using each tokenizer above and answer the following questions:
#   a) What was the total indexing time and how much memory (roughly) is required to index this collection?
#   b) What is your vocabulary size?
#   c) List the ten first terms (in alphabetic order) that appear in only one document (document frequency = 1).
#   d) List the ten terms with highest document frequency.

import Tokenizer

class Indexer:

    def __init__(self, file):
        self.simple_tokenizer = Tokenizer.SimpleTokenizer(file)
        self.better_tokenizer = Tokenizer.BetterTokenizer(file)
        self.shat_table = None