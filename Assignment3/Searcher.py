# Searcher
#  Retrieves documents that contain a given query term from the inverted index.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070


def searchDocuments(queriesTerms, indexFile, withPostitions):

    biggerQueryTerm = sorted(queriesTerms)[-1]
    # indexFile with terms in alphabetical order
    if withPostitions:
        documentsInfo = {}  # {docId: (lenD, {term: (term_idf, logWeight, [pos1, pos2, ...])})}
        docLens = {}  # {docId: len}
        with open(indexFile, 'r') as f:
            line = f.readline()
            print('line: {}'.format(line))
            line = line.replace('\n', '')
            while line != '':
                info = line.split('|')
                print('line.split(\'|\'): {}'.format(info))
                termInfo = info[0].split(':')
                print('termInfo: {}'.format(termInfo))
                print('term_idf: {}'.format(termInfo[-1:][0]))
                term_idf = float(termInfo[-1:][0])
                term = ''.join(termInfo[:-1])  # necessary for terms with ':' in them (like websites)
                print('bqt: {}, query_terms: {}, term: {}'.format(biggerQueryTerm, queriesTerms, term))

                # term not in the beginning or end of a word, like in a hypenate word
                if list(filter(lambda t: t.startswith(term) or t.endswith(term), queriesTerms)) == [] \
                        and term not in queriesTerms: # or term not in queries
                    if term > biggerQueryTerm: # term lexically bigger than query terms
                        break   # no need to continue reading the index, looking for the documents of the query terms
                    else:
                        line = f.readline()
                        continue

                print('term: {}'.format(term))
                del termInfo
                doc_ids = [doc_info.split(':')[0] for doc_info in info[-1:]]
                print('doc_ids: {}'.format(doc_ids))
                term_weights = [doc_info.split(':')[1] for doc_info in info[-1:]]
                print('term_weights: {}'.format(term_weights))
                term_positions = [positions.split(',') for doc_info in info[-1:] for positions in doc_info.split(':')[2]]
                print('term_positions: {}'.format(term_positions))
                for docInd in range(len(doc_ids)):
                    docLens[doc_ids[docInd]] = 1 if doc_ids[docInd] not in docLens.keys() else docLens[doc_ids[docInd]] + 1

                    if doc_ids[docInd] not in documentsInfo.keys():
                        documentsInfo[doc_ids[docInd]] = {}
                        documentsInfo[doc_ids[docInd]][term]: (term_idf,
                                                               float(term_weights[docInd]),
                                                               [int(pos) for pos in term_positions[docInd]])
                    else:
                        documentsInfo[doc_ids[docInd]][term] = (term_idf,
                                                                float(term_weights[docInd]),
                                                                [int(pos) for pos in term_positions[docInd]])

                line = f.readline()
        f.close()
    else:
        documentsInfo = {}  # {docId: (lenD, {term: (term_idf, logWeight)})}
        docLens = {}  # {docId: len}
        with open(indexFile, 'r') as f:
            line = f.readline()
            line = line.replace('\n', '')
            while line != '':
                info = line.split('|')
                termInfo = info[:-1]
                term_idf = float(termInfo[-1:][0])
                term = ''.join(termInfo[:-1])  # necessary for terms with ':' in them (like websites)
                # term not in the beginning or end of a word, like in a hypenate word
                if list(filter(lambda t: t.startswith(term) or t.endswith(term), queriesTerms)) == [] \
                        and term not in queriesTerms:  # or term not in queries
                    if term > biggerQueryTerm:  # term lexically bigger than query terms
                        break  # no need to continue reading the index, looking for the documents of the query terms
                    else:
                        line = f.readline()
                        continue

                del termInfo
                doc_ids = [doc_info.split(':')[0] for doc_info in info[-1:]]
                term_weights = [doc_info.split(':')[1] for doc_info in info[-1:]]
                for docInd in range(len(doc_ids)):
                    docLens[doc_ids[docInd]] = 1 if doc_ids[docInd] not in docLens.keys() else docLens[doc_ids[docInd]] + 1

                    if doc_ids[docInd] not in documentsInfo.keys():
                        documentsInfo[doc_ids[docInd]] = {}
                        documentsInfo[doc_ids[docInd]][term]: (term_idf,
                                                               float(term_weights[docInd]))
                    else:
                        documentsInfo[doc_ids[docInd]][term] = (term_idf,
                                                                float(term_weights[docInd]))

                line = f.readline()
        f.close()

    avgDocLen = sum(docLens.values()) / len(docLens)
    documentsInfo = {docId: (docLens[docId], documentsInfo[docId]) for docId in documentsInfo.keys()}
    return documentsInfo, avgDocLen
