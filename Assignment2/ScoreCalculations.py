import math

# Returns the number of times that the term t occurs in the document d, i.e., the term frequency TF(t,d) of term t
# in document d
#  @param t The term.
#  @param dId The document id.
#  @param postingsMaps map with the terms as keys and as value s map with doc ids as keys and term frequency as value
#  @returns the term frequency TF(t,d) of term t in document d
def getTFtd(t, dId, postingsMaps):
    return 0 if t not in postingsMaps.keys() else postingsMaps[t][dId]

# Returns the number of occurrences of the term t occurs in the collection, counting multiple occurrences
#  @param t The term.
#  @param postingsMaps map with the terms as keys and as value s map with doc ids as keys and term frequency as value
#  @returns the collection frequency of term t
def getCollectionFreq(t, postingsMaps):
    return sum([postingsMaps[t][docId] for docId in postingsMaps[t].keys()])

# Returns the number of documents that contain the term t
#  @param self The object pointer.
#  @param t The term.
#  @param postingsMaps map with the terms as keys and as value s map with doc ids as keys and term frequency as value
#  @returns df(t) - the document frequency of term t
def getDFt(t, postingsMaps):
    return 0 if t not in postingsMaps.keys() else len(postingsMaps[t])

# Returns the inverse document frequency of term t
#  @param self The object pointer.
#  @param t The term.
#  @param postingsMaps map with the terms as keys and as value s map with doc ids as keys and term frequency as value
#  @param N number of documents in the collection
#  @returns idf(t) - the inverse document frequency of term t
def getIDFt(t, postingsMaps, N):
    dft = getDFt(t, postingsMaps)
    dft = 1 if dft == 0 else dft
    return math.log10(N / dft)

# Returns the tf-idf weight of a term in a document (W(t,d))
#  @param self The object pointer.
#  @param t The term.
#  @param dId The document id.
#  @param postingsMaps map with the terms as keys and as value s map with doc ids as keys and term frequency as value
#  @param N number of documents in the collection
#  @returns W(t,d) - the term frequency-inverse document frequency weight of term t in document d
def getTFIDFtWeight(t, dId, postingsMaps, N):
    tf = getTFtd(t, dId, postingsMaps)
    return 0 if tf == 0 else (1 + math.log10(tf)) * getIDFt(t, postingsMaps, N)

def getTFIDFtWeightFromLogWeight(t, postingsMaps, N, logW):
    return logW * getIDFt(t, postingsMaps, N)

def getLogWeight(t, dId, postingsMaps):
    tf = getTFtd(t, dId, postingsMaps)
    return 0 if tf == 0 else (1 + math.log10(tf))

# Returns the tf-idf weight of a term in a document (W(t,d))
#  @param self The object pointer.
#  @param t The term.
#  @param dId The document id.
#  @param postingsMaps map with the terms as keys and as value s map with doc ids as keys and term frequency as value
#  @param N number of documents in the collection
#  @returns W(t,d) - the term frequency-inverse document frequency weight of term t in document d
def getTFIDFtWeightQuery(tf, idf):
    return 0 if tf == 0 else (1 + math.log10(tf)) * idf

def getDocL2Norm(docWeights):
    return math.sqrt(sum([math.pow(weight, 2) for weight in docWeights]))

def getCosine2Docs(docId1, docId2, postingsMaps):
    weightsDoc1 = [postings[docId1] for postings in postingsMaps.values() if docId1 in postings.keys()]
    weightsDoc2 = [postings[docId2] for postings in postingsMaps.values() if docId2 in postings.keys()]
    return sum([w1 * w2 for w1, w2 in zip(weightsDoc1, weightsDoc2)])
