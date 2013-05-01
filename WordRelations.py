from nltk.corpus import wordnet, wordnet_ic
from nltk.corpus.reader.wordnet import WordNetError 
from math import sqrt, pow
from operator import mul


## WebNet perl library
##from perlfunc import perlfunc, perlreq, perl5lib
##@perlfunc
##@perlreq('semantic_dist.pl')
##def semantic_dist(word0, word1):
##    pass


## uses Python NLTK to find semantic distance in WordNet
info_content = wordnet_ic.ic('ic-semcor.dat')
def semantic_dist(word0, word1):
    meanings0 = wordnet.synsets(word0)
    meanings1 = wordnet.synsets(word1)

    distance = None
    for meaning0 in meanings0:
        for meaning1 in meanings1:
            try:
                this_distance = int(1.0/meaning0.path_similarity(meaning1, info_content))
                if this_distance and not distance:
                    distance = this_distance
                else:
                    distance = min(distance, this_distance)
            except WordNetError:
                pass
            except TypeError:
                pass

    return distance


## finds the levenshtein (typographical) distance between words
## used when word meanings are unknown
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


## finds the distances between two phrases using DBpedia
## used to identify pop-culture ties between phrases
def culture_dist(phrase0, phrase1):
    ## TODO: implement this method
    return 9999999999999.


## finds the conceptual distance between two phrases
## using a combination of WordNet semantic distance,
## Levenshtein typographical distance, and 
## DBpedia cultural distance
def phrase_dist(phrase0, phrase1, verbose=False):

    ## finds distance between every pairing
    ## of words from phrase0 to phrase1
    word_distances = {}
    for word0 in phrase0.split():
        for word1 in phrase1.split():
            this_distance = semantic_dist(word0, word1)
            if not this_distance:
                this_distance = levenshtein_dist(word0, word1)+1
            word_distances[(word0, word1)] = this_distance

    if verbose:
        print '\n', phrase0, '<--->', phrase1

    ## average distance from words in phrase0 to words in phrase1
    distances0 = map(lambda word0:  min(map(lambda word1: word_distances[(word0, word1)], phrase1.split())), phrase0.split())
    ## arithmatic mean
    distance0 = float(sum(distances0)) / len(distances0)
    ## geometric mean
##    distance0 = pow(float(reduce(mul, distances0, 1)), 1.0/len(distances0))
    if verbose:
        print '\t', distances0, distance0

    ## average distance from words in phrase1 to words in phrase0
    distances1 = map(lambda word1:  min(map(lambda word0: word_distances[(word0, word1)], phrase0.split())), phrase1.split())
    ## arithmatic mean
    distance1 = float(sum(distances1)) / len(distances1)
    ## geometric mean
##    distance1 = pow(float(reduce(mul, distances1, 1)), 1.0/len(distances1))
    if verbose:
        print '\t', distances1, distance1

    ## use min of phrase0<->phrase1 word pairing distances
##    word_pair_distance = min(distance0, distance1)

    ## use geometric mean of phrase0<->phrase1 word pairing distances
    word_pair_distance = sqrt(distance0 * distance1)

    ## use arithmatic mean of phrase0<->phrase1 word pairing distances
##    word_pair_distance = (distance0 + distance1) / 2.0

    if verbose:
        print '\t', word_pair_distance

    ## distance between phrase0 and phrase1 including cultural contexts
    cultural_distance = culture_dist(phrase0, phrase1)
    
    ## returns the closest conceptual link found
    return min([word_pair_distance, cultural_distance])


if __name__ == "__main__":
    print phrase_dist('versailles garden window'.split(), 'chinese herb garden'.split())
