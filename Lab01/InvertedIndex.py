import Tokenizer
import Indexer

# (modifiedTokens, DocumentId)
pairs = []
docFiles = ["Almeida Garrett - Viagens na Minha Terra.txt", "Eça de Queirós - A Cidade e as Serras.txt"]

for docId in range(len(docFiles)):
    tokenizer = Tokenizer.Tokenizer(docFiles[docId])
    tokenizer.createTokens()

    pairs += [(token, docId) for token in tokenizer.getTokens()]

indexer = Indexer.Indexer(pairs, len(docFiles))
indexer.indexTerms(None)
print("Most frequent terms:")
for docId in range(len(docFiles)):
    print(docFiles[docId] + "\n\t" + str(indexer.getFreqTerms()[docId]))
print("\nMost frequent terms with 4 or more letters:")
indexer.indexTerms(4)
for docId in range(len(docFiles)):
    print(docFiles[docId] + "\n\t" + str(indexer.getFreqTerms()[docId]))