## Indexer
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import CorpusReader
import Tokenizer
import timeit
import psutil
import os
import copy


## Indexer
class Indexer:

    ## The constructor.
    #  @param self The object pointer.
    #  @param collection The path to the csv containing the collection
    #  @param tokenizerType The type of tokenizing to do to each document
    def __init__(self, collection, tokenizerType):
        start = timeit.default_timer()
        self.col = CorpusReader.CorpusReader(collection).readCorpus()  # list((doi, title, abstract))
        self.term_map = {}  # key: term, value: doc_freq_map (key: doi, value: term_freq)
        self.tokenizerType = tokenizerType
        self.termStr = ""

        self.postingsMaps = [] # list of dictionaries for each term, with key: docId, value: term_freq
        self.docFreq = []
        self.termPtrs = []
        self.postingsPtrs = [] # index in postingsMaps
        self.k = 4

        self.index()
        stop = timeit.default_timer()

        #   a) What was the total indexing time?
        print('Indexing time - {} tokenizer: {} seconds'.format("simple" if self.tokenizerType == "0" else "better",
                                                        stop - start))

        # How much memory (roughly) is required to index this collection?
        process = psutil.Process(os.getpid())
        print('\nMemory required for indexing: {} MB'.format(process.memory_info().rss/1000000)) # rss in bytes

        #   b) What is your vocabulary size?
        print('\nVocabulary Size: {}'.format(len(self.docFreq)))

    ## Populates the term_map dictionary with another dictionary with doi's as keys and the term's frequency in that
    # document
    #  @param self The object pointer.
    def index(self):

        for doi, title, abstract in self.col:
            if self.tokenizerType == '0':  # simple
                tokenizer = Tokenizer.SimpleTokenizer(title, abstract)
            else:  # better
                tokenizer = Tokenizer.BetterTokenizer(title, abstract)

            terms = tokenizer.getTerms()

            for term in terms:
                if term in self.termPtrs:
                    if doi in self.postingsMaps[self.termPtrs.index(term)].keys():
                        self.postingsMaps[self.termPtrs.index(term)][doi] += 1
                    else:
                        self.docFreq[self.termPtrs.index(term)] += 1
                        self.postingsMaps[self.termPtrs.index(term)][doi] = 1
                else:
                    self.termPtrs += [term]
                    self.postingsPtrs += [len(self.termPtrs) - 1]
                    term_freq_map = {}  # key: docId, value: term_freq
                    term_freq_map[doi] = 1
                    self.postingsMaps += [term_freq_map]
                    self.docFreq += [1]

        self.dictionaryCompression()

    ## Lists the ten first terms (in alphabetic order) that appear in only one document (document frequency = 1).
    #  @param self The object pointer.
    def listTermsInOneDoc(self):
        terms = [self.getTermFromDictStr(termPtr) for termPtr in self.termPtrs]
        results = [term for term in sorted(terms) if self.docFreq[terms.index(term)] == 1]
        print('\nTen first Terms in only 1 document: \n{}'.format(results[:10]))

    ## Lists the ten terms with highest document frequency.
    #  @param self The object pointer.
    def listHighestDocFreqTerms(self):
        terms = [self.getTermFromDictStr(termPtr) for termPtr in self.termPtrs]
        doc_freq = sorted(terms, key=lambda term: self.docFreq[terms.index(term)], reverse=True)
        print('\nTen terms with highest document frequency: \n{}'.format(doc_freq[:10]))

    # The search begins with the dictionary.
    # We want to keep it in memory .
    # Even if the dictionary isn't in memory, we want it to be small for a fast search start up time
    def dictionaryCompression(self):

        # terms in alphabetical order
        self.postingsMaps = [pm for _, pm in sorted(zip(self.termPtrs, self.postingsMaps))]
        self.docFreq = [df for _, df in sorted(zip(self.termPtrs, self.docFreq))]
        self.postingsPtrs = [pp for _, pp in sorted(zip(self.termPtrs, self.postingsPtrs))]
        self.termPtrs = sorted(self.termPtrs)
        terms = copy.copy(self.termPtrs)
        # store dictionary as a (long) string of characters with the length of each term preceding it
        self.termStr = ""
        # Because there is no pointers in python, we store the position of the length of the term in the string as a
        # pointer to were the term is located in the string
        termPtr = None
        # front coding - sorted words commonly have long common prefix-store differences only
        # example: 8automata8automate9automatic10automation  becomes: 8automat*a1|e2|ic3|ion
        encodedTerm = ""
        # TODO: remove * and | from tokenizer

        for i in range(len(terms)):
            termPtr = len(self.termStr)
            self.termPtrs[i] = termPtr  # new values in the list are "pointers" to terms / delete terms from the list

            lenTerm = str(len(terms[i]))
            prefixLen = 0
            # last term had a prefix common with another term, and the current one starts with that same prefix
            if encodedTerm != "" and terms[i].startswith(encodedTerm):
                # extraLength | remainPartOfTheTerm, e.g.: 1|e
                self.termStr += str(len(terms[i][len(encodedTerm):])) + "|" + terms[i][len(encodedTerm):]
            # last term and the current one have no common prefix
            elif i <= len(terms) - 2:
                # e.g.: 8
                self.termStr += lenTerm
                # evaluate if there is a common prefix with the next term
                while (True):
                    if prefixLen == len(terms[i]) or terms[i][prefixLen] != terms[i + 1][prefixLen]:
                        break
                    prefixLen += 1
                # only encode terms with common prefixes with more than 3 characters
                if prefixLen > 3:
                    encodedTerm = terms[i][:prefixLen]
                    self.termStr += encodedTerm + '*' + terms[i][prefixLen:]
                else:
                    self.termStr += terms[i]
                    encodedTerm = ""
            # last term with no shared prefix
            else:
                self.termStr += lenTerm + terms[i]
                encodedTerm = ""


        '''
        # terms in alphabetical order
        terms = sorted(list(self.term_map.keys()))

        # store dictionary as a (long) string of characters with the length of each term preceding it
        self.termStr = ""
        # Because there is no pointers in python, we store the position of the length of the term in the string as a
        # pointer to were the term is located in the string
        termPtr = None
        # front coding - sorted words commonly have long common prefix-store differences only
        # example: 8automata8automate9automatic10automation  becomes: 8automat*a1|e2|ic3|ion
        encodedTerm = ""
        # TODO: remove * and | from tokenizer
        for i in range(len(terms)):
            termPtr = len(self.termStr)
            self.term_map[termPtr] = self.term_map[terms[i]] # new keys are "pointers"
            del self.term_map[terms[i]] # delete terms from keys

            lenTerm = str(len(terms[i]))
            prefixLen = 0
            # last term had a prefix common with another term, and the current one starts with that same prefix
            if encodedTerm != "" and terms[i].startswith(encodedTerm):
                # extraLength | remainPartOfTheTerm, e.g.: 1|e
                self.termStr += str(len(terms[i][len(encodedTerm):])) + "|" + terms[i][len(encodedTerm):]
            # last term and the current one have no common prefix
            elif i <= len(terms) - 2 :
                # e.g.: 8
                self.termStr += lenTerm
                # evaluate if there is a common prefix with the next term
                while(True):
                    if prefixLen == len(terms[i]) or terms[i][prefixLen] != terms[i+1][prefixLen]:
                        break
                    prefixLen += 1
                # only encode terms with common prefixes with more than 3 characters
                if prefixLen > 3:
                    encodedTerm = terms[i][:prefixLen]
                    self.termStr += encodedTerm + '*' + terms[i][prefixLen:]
                else:
                    self.termStr += terms[i]
                    encodedTerm = ""
            # last term with no shared prefix
            else:
                self.termStr += lenTerm + terms[i]
                encodedTerm = ""
        '''

    def getTermFromDictStr(self, termPtr):
        #termStr = "4AJPH4ASFV3BPI3CAD5COVID4CRAN3CRD3CRO12Central-West5China34Contactwilliam.ritchie@igh.cnrs.fr3DOI3DUX4EV-G7Fuk-Woo3HCT3HCW3HIV4HRCT3IAV5IFITM3JIA14Jean-Christoph4KCDC4MERS*4|-CoV3NCP3OSF4PAPR4PEDV4PLVP3PRF8PROSPERO3QHO3RBD6RETURN3RNA11S-palmitoyl4SARS*4|-CoV4SFTS3SRP4TEXT3UXT3WHO4ZIKV6abroad8abstract5abund6accord5accur*3|aci14acetobutylicum6achiev4acid4acnv5activ7address6affect6africa9afterward5agent6aggreg4alon5alter6analy*s1|z4anim8anti*bodi3|gen3|vir8appendix6applic8approach5april11archi*tectur1|v4area6articl4asia6aspect5assay9asse*mblag2|ss6associ10asymptomat6attent6author5avail9avirus-no10background8bacteria3bad7barrier3bat8bauchner7beamlin5begin8behavior8benefici6beyond8bhadelia4bias6biolog4bodi3bog6border5brain9brazilian12bronchoscopi5broth6burden6canada6cancer6candid*4|emia4care*1|r8carnivor4case4cell5chain8challeng5chang5chest5child*3|ren5chin*a2|es10chloroquin5choic8circumst7classif5clear*3|anc2|er9clinician6closur9co-infect8co-ordin5codon8colleagu3com6combin7comm*iss4|unic5|uniti8comorbid6comp*ar4|ound6|rehens7concern6condit7confirm6cons*id6|ortium7conta*ct2|in7cont*inu4|ract3|rol11coronavirus11cost-effect5count*8|ermeasur2|ri3cov5crisi6cryoem4cure4cycl9cyranoski5damag4data*3|bas4date3day5death5deduc5delay8deliveri5dengu6depart7desc*ent3|rib6design8destruct6detect7develop5deyin8diagnos*i1|t3die8disc*harg2|ov5|rimin3|uss6diseas6disord9distribut6domain6dramat4drug5dynam4educ6effect6effici6effort5elder7element5emerg11endonucleas5engin5entri7environ5enzym6epidem*5|iolog8|iologist8epilepsi10epithelium5equal4erad5escap5estim7etiolog5evalu5event*1|u4evid6evol*ut1|v7exacerb6exampl4exit6expert6explos7exposur7express7fallout6famili3far7fashion4fast5fatal6favour7feasibl6featur8februari5femal6fertil5fidel3fig5fight4find3fit10flavivirus3fmw6forens5found*2|at10frameshift8fulltext8function4fund5futur4gard4gene*3|ral5genom5genus11ghebreyesus6github6glob*al1|e12glycoprotein4goal4good5group4grow*2|th6guanin8guidelin7habitat8haplotyp6happen6health*1|i4help9highlight4hive10homeostasi6hospit4host3hsp28http://c*ovdb.popgenetics.net38|ran.r-project.org/web/packages/metaMix26http://*korkinlab.org/wuhan51|service.tartaglialab.com//new_submission/CROSSalign16https://*Scite.ai20|adapt.sabetilab.org/46|doi.org/10.2807/1560-7917.ES.2020.25.9.200017867|eurosurveillance.org/content/10.2807/1560-7917.ES.2020.25.9.200015267|eurosurveillance.org/content/10.2807/1560-7917.ES.2020.25.9.200305124|github.com/B-UMMI/DEN-IM56|github.com/chjiao/VirBin\n\nContactyannisun@cityu.edu.hk35|github.com/galaxyproject/SARS-CoV-225|github.com/mriglobal/vorp23|github.com/rcs333/VAPiD26|gitlab.com/rki_bioinformat24|life.bsc.es/pid/skempi2/28|virusgateway.readthedocs.io/82|www.who.int/health-topics/coronavirus/laboratory-diagnostics-for-novel-coronavirus5hubei5human6hygien8identifi5ignor3ill6immedi5immun*9|opatholog8|otherapi6impa*ct2|ir9implement6import5incur5indi*c4|vidu12|vidual-level6infect9influenza13infrastructur9inhibitor6inject6injuri7insight7inst*abl4|itut8inter*est3|fac5|feron1|n4|pret4|vent8investig6involv4iran4isol4item7januari5japan6jasper3jat7journal4june5kinas13kinetoplastid3kit5klein5known4kong5korea9kucharski8landscap4larg6lesion4less5level7liberti6licens4life4like5limit4link4list5live*r5|stock4long4loss3low5lucet8mackenzi4made8maintain10malassezia5manag6manner5march8maryland6measur6mechan5medi*a1|c3|cin6member6memori8metazoan6method11micro*biolog4|glia4mild5minim5mirna9misinform7mislead5modal5model6moieti7molecul7monitor5month6mortal8movement4mpro5mrnas5mucus7municip6mutant8mycetoma8nabbrevi4name10nanosensor4nbsp4ncov3ncp5ncrna5nebul9necessari7necrosi4need3nef6neonat7network11neurologist9non-sever4none4nose6notion6novemb3now4nurs6object6observ5occur5offic3one5onlin5onset6onward4opac*2|if5optim5organ6origin5other8outbreak6outcom10overemphas4page8pakistan6pandem5paper10particular4path*4|ogen7|ogenesi4|olog7patient*2|en7pattern7peacock4peak5peopl7perform6period9permissiv6person*3|nel9physician4piec3pig6piglet7pilgrim9place-for4plan9pneumonia6podigi6polic*i5|y-mak5popul5posit7possibl7postnat7potenti8poxvirus7practic7predict8pregnanc8prepared7pres*ent3|sur7prevent8prioriti7prob*abl3|lem7process10profession8prog*nosi4|ress8prolifer6promot8properti7prote*ct2|in2|om7prot*ist4|ocol6provi*d2|nc6publi*c2|sh8quantiti9quarantin8question*4|nair12racism-xenop10radiograph4rang4rare4rate4read8real-tim5recal6recipi8recom*bin4|mend8recoveri6redakt7regi*men2|on3|str5regul9rehabilit5relat6reliev6replic6report6requir8rese*arch2|rv5resi*d2|st7resourc7resp*ect3|ond3|ons8restrict6result6revers6review4risk7rnajena7rosetta4rout4said5sampl4scan13schizophrenia6screen6search6season5secur6select7sequenc4serv3set3sev5sever4shen*4|zhen4ship4sign*2|al4|ific4site6situat4size4solv6someth5sourc5speci*1|f6spread*2|er5staff5stage5state6stimul10stomatolog5storm6stra*in4|tegi10strengthen8striatum8structur5studi7submiss7suggest10supplement6surfac8surround7surv*eil2|iv7suscept4swab7symptom7syndrom6system4tabl44tagashira_masaki_17@stu-cbms.k.u-tokyo.ac.jp5taken6target5teach4team9technolog6tengyu6termin4test9therap*eut1|i7therein8thorough6threa*d1|t4time6togeth4tool5tract5train12trans*criptom3|lat4|miss6travel9treatment5trend5trial7truncat5trust3two4type7undergo6unfold7unknown3use6vaccin5valid4valu6vector7version5viral5viro*m5|plasm5viru*l1|s5vital4vivo4ward7warrant4wave3way6webpag6websit4week6welcom4well5women4work*2|er5world*3|wid7written5wuhan29www.seattleflu.org).</jats:p>4year7zealand8zhejiang6zoonos"
        #termPtrs = [0, 5, 10, 14, 18, 24, 29, 33, 37, 51, 57, 93, 97, 101, 106, 114, 118, 122, 126, 131, 135, 141, 145, 161, 166,         172, 178, 182, 186, 191, 196, 201, 205, 214, 218, 222, 229, 233, 246, 252, 258, 263, 267, 272, 276, 280, 285,         292, 301, 307, 314, 321, 326, 342, 349, 354, 359, 365, 373, 380, 387, 397, 403, 410, 415, 421, 429, 432, 437,         447, 452, 457, 466, 473, 482, 488, 502, 505, 510, 517, 522, 529, 535, 546, 550, 557, 569, 576, 583, 589, 599,         611, 620, 624, 632, 636, 645, 653, 659, 668, 677, 684, 693, 698, 705, 710, 714, 721, 727, 737, 751, 757, 764,         771, 778, 786, 792, 798, 801, 810, 815, 820, 826, 835, 841, 847, 854, 859, 866, 870, 882, 888, 897, 905, 912,         917, 921, 931, 938, 948, 957, 963, 972, 976, 983, 992, 998, 1005, 1014, 1022, 1028, 1036, 1044, 1051, 1059,         1067, 1075, 1084, 1088, 1097, 1103, 1108, 1121, 1134, 1141, 1151, 1155, 1159, 1165, 1172, 1177, 1182, 1192,         1198, 1204, 1209, 1214, 1218, 1224, 1230, 1236, 1245, 1251, 1258, 1267, 1272, 1279, 1288, 1295, 1303, 1309,         1319, 1322, 1326, 1336, 1340, 1347, 1352, 1359, 1366, 1376, 1383, 1390, 1395, 1401, 1406, 1413, 1420, 1427,         1433, 1441, 1447, 1460, 1466, 1472, 1480, 1486, 1494, 1501, 1511, 1520, 1532, 1538, 1543, 1549, 1555, 1563,         1569, 1576, 1579, 1584, 1592, 1595, 1603, 1610, 1615, 1622, 1629, 1637, 1645, 1653, 1660, 1664, 1672, 1677,         1683, 1690, 1698, 1705, 1714, 1720, 1727, 1733, 1737, 1743, 1748, 1752, 1764, 1768, 1775, 1782, 1786, 1798,         1807, 1816, 1821, 1827, 1832, 1838, 1843, 1849, 1855, 1868, 1875, 1883, 1886, 1900, 1905, 1910, 1916, 1922,         1926, 1933, 1942, 1950, 1959, 1966, 1974, 1977, 1982, 1992, 1997, 2009, 2016, 2021, 2025, 2056, 2097, 2126,         2180, 2199, 2222, 2271, 2341, 2411, 2438, 2497, 2535, 2563, 2589, 2618, 2645, 2676, 2761, 2767, 2773, 2780,         2789, 2795, 2799, 2806, 2813, 2824, 2834, 2842, 2846, 2856, 2863, 2869, 2876, 2882, 2897, 2904, 2914, 2929,         2939, 2946, 2953, 2961, 2970, 2976, 2986, 2991, 2998, 3001, 3007, 3013, 3022, 3029, 3034, 3039, 3044, 3052,         3058, 3065, 3069, 3077, 3082, 3088, 3103, 3107, 3113, 3119, 3124, 3130, 3140, 3149, 3154, 3161, 3166, 3172,         3180, 3187, 3192, 3197, 3203, 3208, 3213, 3220, 3227, 3232, 3237, 3241, 3247, 3256, 3261, 3270, 3282, 3288,         3295, 3301, 3310, 3317, 3324, 3331, 3334, 3339, 3346, 3353, 3362, 3369, 3383, 3389, 3394, 3400, 3406, 3416,         3424, 3430, 3436, 3443, 3451, 3459, 3465, 3472, 3481, 3486, 3492, 3498, 3506, 3513, 3522, 3531, 3536, 3548,         3553, 3558, 3562, 3568, 3574, 3584, 3592, 3597, 3601, 3608, 3616, 3629, 3639, 3644, 3649, 3656, 3663, 3667,         3672, 3679, 3686, 3692, 3698, 3702, 3708, 3714, 3721, 3727, 3731, 3737, 3743, 3750, 3756, 3765, 3772, 3784,         3789, 3798, 3805, 3811, 3823, 3829, 3835, 3844, 3850, 3859, 3863, 3871, 3879, 3884, 3890, 3898, 3905, 3915,         3923, 3928, 3938, 3943, 3947, 3954, 3962, 3972, 3977, 3987, 3994, 4002, 4009, 4015, 4021, 4029, 4037, 4045,         4054, 4062, 4070, 4079, 4088, 4097, 4102, 4110, 4119, 4128, 4133, 4141, 4153, 4163, 4169, 4178, 4185, 4194,         4203, 4207, 4211, 4220, 4226, 4234, 4238, 4246, 4250, 4259, 4269, 4279, 4285, 4299, 4311, 4316, 4321, 4326,         4331, 4340, 4346, 4353, 4363, 4369, 4378, 4385, 4394, 4398, 4403, 4409, 4419, 4425, 4432, 4439, 4446, 4453,         4463, 4467, 4474, 4478, 4486, 4495, 4500, 4505, 4514, 4521, 4528, 4535, 4540, 4548, 4556, 4561, 4566, 4572,         4577, 4592, 4599, 4606, 4613, 4619, 4626, 4634, 4639, 4643, 4647, 4653, 4659, 4665, 4670, 4676, 4680, 4686,         4691, 4698, 4703, 4708, 4715, 4721, 4728, 4731, 4739, 4743, 4749, 4755, 4761, 4768, 4780, 4786, 4794, 4800,         4812, 4821, 4830, 4836, 4844, 4852, 4864, 4871, 4880, 4889, 4893, 4901, 4906, 4914, 4922, 4929, 4934, 4980,         4986, 4993, 4999, 5004, 5014, 5021, 5028, 5033, 5044, 5047, 5055, 5064, 5072, 5075, 5080, 5087, 5092, 5098,         5104, 5119, 5124, 5130, 5137, 5147, 5153, 5159, 5167, 5173, 5177, 5182, 5190, 5197, 5205, 5209, 5216, 5222,         5227, 5234, 5242, 5248, 5255, 5262, 5269, 5272, 5278, 5283, 5288, 5296, 5301, 5305, 5312, 5319, 5324, 5331,         5336, 5342, 5348, 5352, 5359, 5364, 5372, 5378, 5409, 5414, 5422, 5431]

        lenInPtr = ""
        nDigitLen = 0
        while(True):
            lenInPtr += self.termStr[termPtr+nDigitLen]
            nDigitLen += 1
            if not self.termStr[termPtr+nDigitLen].isdigit():
                nDigitLen -= 1
                break
        lenInPtr = int(lenInPtr)

        newPtr = termPtr + nDigitLen
        extraLength = lenInPtr if self.termStr[newPtr+1] == '|' else 0

        if extraLength == 0:
            term = self.termStr[newPtr+1:newPtr+1+lenInPtr]
            if '*' in term:
                term.replace('*','')
                # Discover extra part of the word
                term += self.termStr[newPtr+1+lenInPtr]
        else:
            # Discover base word
            endBaseWord = 1
            while(True):
                char = self.termStr[newPtr - endBaseWord]
                if char == '*':
                    break
                endBaseWord += 1

            startBaseWord = endBaseWord
            while(True):
                char = self.termStr[newPtr - startBaseWord]
                if char.isdigit():
                    startBaseWord -= 1
                    term = self.termStr[newPtr - startBaseWord : newPtr - endBaseWord]
                    break
                startBaseWord += 1

            # Discover extra part of the word
            term += self.termStr[newPtr+2:extraLength]

        return term

    def postingsGammaEncoded(self):
        pass