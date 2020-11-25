# Gamma Decoder.
#  For posting decoding purposes.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

# Gamma Decoder
class GammaDecoder:

    # The constructor.
    #  @param self The object pointer.
    def __init__(self, fileName):
        self.fileName = fileName
        self.readBitsFromFile()

    def readBitsFromFile(self):
        binaryToRead = ""
        with open(self.fileName, 'rb') as f:
            byte = f.read(1)
            binaryToRead += "{0:b}".format(int.from_bytes(byte, byteorder='big'))
            while byte:
                byte = f.read(1)
                binaryToRead += "{0:b}".format(int.from_bytes(byte, byteorder='big'))

        f.close()

    def decodePostingsFromTerm(self, postingsPtr):
        pass