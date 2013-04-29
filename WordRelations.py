##from perlfunc import perlfunc, perlreq, perl5lib
from nltk.corpus import wordnet, wordnet_ic
from nltk.corpus.reader.wordnet import WordNetError 

##@perlfunc
##@perlreq('semantic_dist.pl')
##def semantic_dist(word0, word1):
##    pass


info_content = wordnet_ic.ic('ic-semcor.dat')

def semantic_dist(word0, word1):
    meanings0 = wordnet.synsets(word0)
    meanings1 = wordnet.synsets(word1)

    similarity = 0.0
    for meaning0 in meanings0:
        for meaning1 in meanings1:
            try:
                similarity = max(similarity, meaning0.lin_similarity(meaning1, info_content))
            except WordNetError:
                pass

    return similarity


## @author Magnus Lie Hetland
## courtesy http://hetland.org/coding/python/levenshtein.py
def levenshtein_dist(word0, word1):
    n, m = len(word0), len(word1)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        word0, word1 = word1,word0
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if word0[j-1] != word1[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]


def phrase_dist(phrase0, phrase1):
    ## TODO implement this method
    return 0


if __name__ == "__main__":
    print semantic_dist('cat', 'dog')
##    print semantic_dist('cat#n#1', 'dog#n#1')
