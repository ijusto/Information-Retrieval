# Searcher
#  Retrieves documents that contain a given query term from the inverted index.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

def searchDocuments(queriesTerms, indexFile):
    documentsInfo = {} # {docId: lenD, {term: (term_idf, logWeight)}}
    docLens = {} # {docId: len}
    with open(indexFile, 'r') as f:
        line = f.readline()
        while line != '':
            info = line.split(';')
            term, term_idf = info[0].split(':')

            for doc in info[1:]:
                docId, logWeight = doc.split(':')
                docLens[docId] = 1 if docId not in docLens.keys() else docLens[docId] + 1
                for termQuery in queriesTerms:
                    if termQuery == term:
                        documentsInfo[docId] = {} if docId not in documentsInfo.keys() \
                                                  else {termQuery : (term_idf, logWeight)}

            line = f.readline()
    f.close()
    avgDocLen = sum(docLens.values()) / len(docLens)
    documentsInfo = [(docLens[docId], documentsInfo[docId]) for docId in documentsInfo.keys()]
    return documentsInfo, avgDocLen

# def searchForTermInDictionary(self, t):
#     for ptrInd in range(len(self.termPtrs)):
#         blockPtr = self.termPtrs[ptrInd]
#         baseWord = ""
#         termPtr = blockPtr
#         lenInPtrStr = ""
#         nDigitLen = 0
#         while True:
#             lenInPtrStr += self.dictionary[termPtr + nDigitLen]
#             nDigitLen += 1
#             if not self.dictionary[termPtr + nDigitLen].isdigit():
#                 nDigitLen -= 1
#                 break
#         lenInPtr = int(lenInPtrStr)
#
#         newPtr = termPtr + nDigitLen
#
#         term = self.dictionary[newPtr + 1:newPtr + 1 + lenInPtr]
#
#         termPtr = newPtr + 1 + lenInPtr
#         if '*' in term:
#             term = term.replace('*', '')
#             # Discover extra part of the word
#             term += self.dictionary[newPtr + 1 + lenInPtr]
#             termPtr += 1
#         elif newPtr + 1 + lenInPtr < len(self.dictionary) - 1 and '*' in self.dictionary[newPtr + 1 + lenInPtr]:
#             termPtr += 1
