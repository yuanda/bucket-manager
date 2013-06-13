## python modules
from nltk.corpus import wordnet, wordnet_ic
from nltk.corpus.reader.wordnet import WordNetError 
from math import sqrt, pow
from operator import mul

## local modules
from dbpedia import *


## public db for topic lookup
TOPIC_LOOKUP_URL = 'http://lookup.dbpedia.org/api'

## adaptly's db for topic lookup
##TOPIC_LOOKUP_URL = 'http://ec2-50-16-51-14.compute-1.amazonaws.com:1111/api'

## adaptly's semantic web
SEMANTIC_WEB_URL = 'http://ec2-54-234-151-173.compute-1.amazonaws.com:7474/db/data'


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
    topics0 = dbpedia_lookup(phrase0, TOPIC_LOOKUP_URL)
    topics1 = dbpedia_lookup(phrase1, TOPIC_LOOKUP_URL)

    min_dist = None
    for topic0 in topics0:
        for topic1 in topics1:
            this_dist = shortestPath(topic0, topic1)

            if not min_dist or this_dist < min_dist:
                min_dist = this_dist

    return min_dist


## finds the conceptual distance between two phrases
## using a combination of WordNet semantic distance,
## Levenshtein typographical distance, and 
## DBpedia cultural distance
def phrase_dist(phrase0, phrase1, verbose=False):

    ## finds distance between every pairing
    ## of words from phrase0 to phrase1
    word_distances = []
    for word0 in phrase0.split(' '):
        for word1 in phrase1.split(' '):
            this_distance = semantic_dist(word0, word1)
            if not this_distance:
                this_distance = levenshtein_dist(word0, word1)+1
            word_distances.append(this_distance)

    if verbose:
        print '\n', phrase0, '<--->', phrase1

    ## use arithmatic mean of word pairing distances
    word_pair_distance = sum(word_distances) / float(len(word_distances))

    if verbose:
        print '\t', word_pair_distance

    ## distance between phrase0 and phrase1 including cultural contexts
    cultural_distance = culture_dist(phrase0, phrase1)
    
    ## returns the closest conceptual link found
    return min([word_pair_distance, cultural_distance])


if __name__ == "__main__":
    print phrase_dist('diving', 'scuba', verbose=True)
