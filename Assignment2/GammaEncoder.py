# Gamma Encoder.
#  For posting encoding purposes.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

# Gamma Encoder
class GammaEncoder:

    # The constructor.
    #  @param self The object pointer.
    def __init__(self, postingsList):
        self.postingsList = postingsList

    def encodeAndWritePostings(self, filename):
        postingsFile = open(filename, 'wb')

        postingsPtrs = []
        binaryToWrite = ""
        for postings in self.postingsList:
            postingsPtrs += [len(binaryToWrite)]
            gap = 0
            for docId in postings:
                gap = docId - gap
                binaryToWrite += self.encode(gap)

        while True:
            if len(binaryToWrite) < 8:
                binaryToWrite += "0"*(8 - len(binaryToWrite))
                postingsFile.write(bytes([int(binaryToWrite, 2)]))
                break
            postingsFile.write(bytes([int(binaryToWrite[:8], 2)]))
            binaryToWrite = binaryToWrite[8:]

        postingsFile.close()
        return postingsPtrs

    def encode(self, G):
        return '1'*len("{0:b}".format(G)[1:]) + '0' + "{0:b}".format(G)[1:]
