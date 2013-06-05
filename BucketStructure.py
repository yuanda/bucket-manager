## local modules
from WordRelations import *

## python modules
import sys
import hashlib
import json


## holds the words in a bucket
## can calculate and store the relationships between those words,
## as well as outputting data in a format friendly to the app
class BucketStructure:

    ## words are stored in the structure dict as a csv, using this as a separator
    WORD_SEPARATOR = '&$&'

    ## constructor
    ## words - list of keywords in the bucket
    def __init__(self, words=[]):
        self.words = sorted(words)

        ## caluculates the hash key for the bucket using its contents
        tmp = hashlib.md5()
        tmp.update(json.dumps(self.words))
        hash_key = tmp.hexdigest()

        ## structure for the bucket
        ## analagous to bucket node properties in neo4j database
        self.structure = {'WORDS__':self.WORD_SEPARATOR.join(self.words), 'HASH__':hash_key}
        self.words = set(self.words)


    ## returns list of all bucket keywords
    def getWords(self):
        return self.words


    ## returns bucket hash key
    def getHash(self):
        return self.structure.get('HASH__', None)


    ## returns relatedness of two keywords in the bucket
    def getEdge(self, word0, word1):
        edge_key = self.wordHash(word0, word1)
        return self.structure.get(edge_key, None)


    ## sets relatedness of two keywords in the bucket
    def setEdge(self, word0, word1, edge_value):
        self.words.add(word0)
        self.words.add(word1)
        self.structure['WORDS__'] = self.WORD_SEPARATOR.join(self.words)
        edge_key = self.wordHash(word0, word1)
        self.structure[edge_key] = edge_value


    ## loads a saved bucket structure
    ## usually the properties of a bucket node from the neo4j database
    def loadStructure(self, saved_structure):
        self.structure = saved_structure
        self.words = self.structure.get('WORDS__', '').split(self.WORD_SEPARATOR)


    ## returns all structure data
    def dumpStructure(self):
        return self.structure


    ## returns a single bucket stat, if present
    def getStat(self, statname):
        return self.structure.get(statname, None)


    ## sets a single bucket stat
    def setStat(self, statname, value):
        self.structure[statname] = value


    ## calculates the relatedness among all keywords
    def calculateEdges(self):
        for word0 in self.words:
            ## finds relatedness with all other words
            word0_edge_lengths = []
            for word1 in self.words:
                if not word0 == word1:
                    edge_length = phrase_dist(word0, word1, verbose=False)
                    self.structure[self.wordHash(word0, word1)] = phrase_dist(word0.strip('#'), word1.strip('#'), verbose=False)
                    word0_edge_lengths.append(edge_length)

            ## finds centrality based on average relatedness
            ## arithmatic mean of distances
            word0_centrality = float(sum(word0_edge_lengths)) / len(word0_edge_lengths)
            ## geometric mean of distances
##            word0_centrality = pow(reduce(mul, word0_edge_lengths, 1), 1.0/len(word0_edge_lengths))
            self.structure['CENTRALITY__' + word0] = word0_centrality


    ## returns an app friendly version of the relatedness among all keywords
    def dumpEdges(self):
        word_list = list(self.words)
        edges = {}
        nwords = len(word_list)

        for word0_ind in range(1, nwords):
            for word1_ind in range(0, word0_ind):
                word0 = word_list[word0_ind]
                word1 = word_list[word1_ind]
                edge_key = self.wordHash(word0, word1)
                if edge_key in self.structure:
                    edges[(word0, word1)] =  self.structure[edge_key]

        return edges


    ## returns an app friendly version of the semantic centrality of each keyword
    def dumpCentrality(self):
        nodes = {}
        centrality_keys = filter(lambda k: k[0:12] == 'CENTRALITY__', self.structure.keys())
        for key in centrality_keys:
            nodes[key[12:]] = self.structure[key]
        return nodes


    ## returns an app friendly version of all stored bucket stats
    def dumpStats(self):
        stats = {}
        stat_keys = filter(lambda k: not (k[0:6] == 'EDGE__') and not (k[0:12] == 'CENTRALITY__'), self.structure.keys())
        for key in stat_keys:
            stats[key] = self.structure[key]
        return stats 


    ## returns a unique hash key for keyword pair
    def wordHash(self, word0, word1):
        return "EDGE__" + str((hash(word0) + hash(word1)) % sys.maxint)



if __name__ == "__main__":
    x = BucketStructure(words=[ \
                                  'cats', \
                                  'cats kittens', \
                                  'cats eye', \
                                  'cats eyes', \
                                  'kittens', \
                                  'kitties', \
                                  'stray cats', \
                                  'kittens cats', \
                                  'kitty', \
                                  'kitty cats', \
                                  'felines', \
                                  'feline friends cat sanctuary', \
                                  'tabby cat', \
                                  'tabby cats', \
                                  'tabby', \
                                  'orange tabby cats', \
                                  'house cat', \
                                  'cat house', \
                                  'cat toys', \
                                  'calico cats', \
                                  'tortoiseshell calico cats', \
                                  'black cats', \
                                  'siamese cats', \
                                  'siamese cat', \
                                  'cat lovers we love our pets', \
                                  'cat lover', \
                                  'cat lovers day', \
                                  'cat lovers', \
                                  'i love cats', \
                                  'i love my cat', \
                                  'we love cats', \
                                  'petling cat', \
                                  'cat petting', \
                                  'petting cats', \
                                  'petting my cat', \
                                  'petting my cats'
                              ])
    x.calculateEdges()
##    print x.dumpEdges()
    for line in sorted(x.dumpCentrality().items(), key=lambda k: k[1]):
        print line
    print x.dumpStats()
