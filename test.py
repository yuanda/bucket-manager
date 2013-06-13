from nltk.corpus import wordnet, wordnet_ic
from nltk.corpus.reader.wordnet import WordNetError

from time import *
from threading import *


if __name__ == "__main__":

    word0 = 'dog'
    word1 = 'cat'

    x = wordnet.synsets(word0)
    y = wordnet.synsets(word1)

    NTRIALS = 1000

    ic = wordnet_ic.ic('ic-semcor.dat')

    ## find similarity, catch pos errors
    starttime = time()
    print 'catch:'
    for trial in range(0, NTRIALS):
        for i in x:
            for j in y:
                try:
                    i.lin_similarity(j, ic)
                except Exception as e:
                    print type(e), e.message
    print '\t', (time() - starttime)/NTRIALS, 'sec per trial'


    ## check pos, then find similarity
    starttime = time()
    print 'check:'
    for trial in range(0, NTRIALS):
        for i in x:
            for j in y:
                if i.name.split('.')[1] == j.name.split('.')[1]:
                    i.lin_similarity(j, ic)
    print '\t', (time() - starttime)/NTRIALS, 'sec per trial'



