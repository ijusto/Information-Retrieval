# Searcher
#  Retrieves documents that contain a given query term from the inverted index.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070


def searchDocuments(queriesTerms, indexFile):
    documentsInfo = {}  # {docId: lenD, {term: (term_idf, logWeight)}}
    docLens = {}  # {docId: len}
    # terms ordered by idf (rarer terms are more important)
    # and documents inside the term dictionary by weight, so we can exclude the inferior weight terms
    numberOfDocuments = 70
    with open(indexFile, 'r') as f:
        line = f.readline()
        while line != '':
            info = line.split('|')
            info.remove('\n')
            termInfo = info[0].split(':')
            term_idf = float(termInfo[-1:][0])
            term = ''.join(termInfo[:-1])  # necessary for terms with ':' in them (like websites)
            for doc in info[1:]:
                docId, logWeight = doc.split(':')
                docLens[docId] = 1 if docId not in docLens.keys() else docLens[docId] + 1

                if term in queriesTerms:
                    if docId not in documentsInfo.keys():
                        numberOfDocuments -= 1
                        documentsInfo[docId] = {}
                        documentsInfo[docId][term]: (term_idf, float(logWeight))
                    else:
                        documentsInfo[docId][term] = (term_idf, float(logWeight))

                if numberOfDocuments == 0:
                    break

            if numberOfDocuments == 0:
                break
            line = f.readline()
    f.close()
    avgDocLen = sum(docLens.values()) / len(docLens)
    documentsInfo = {docId: (docLens[docId], documentsInfo[docId]) for docId in documentsInfo.keys()}
    return documentsInfo, avgDocLen
