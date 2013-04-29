import sys


class BucketStructure:

    def __init__(self, words=[]):
        self.words = set(words)
        self.structure = {}


    def getWords():
        return self.words


    def getEdge(word0, word1):
        edge_key = self.wordHash(word0, word1)
        return self.structure.get(edge_key, None)


    def setEdge(word0, word1, edge_value):
        self.words.add(word0)
        self.words.add(word1)
        edge_key = self.wordHash(word0, word1)
        self.structure[edge_key] = edge_value


    def loadStructure(saved_structure):
        self.structure = saved_structure


    def dumpStructure():
        return self.structure


    def calculateEdges():
        for word0 in self.words:
            for word1 in self.words:
                if not word0 == word1:
                    self.structure[wordHash(word0, word1)] = phrase_dist(word0, word1)


    def getStat(statname):
        return self.structure.get(statname, None)


    def dumpEdges():
        edges = []
        nwords = len(self.words)

        for word0_ind in range(1, nwords):
            for word1_ind in range(0, word0_ind):
                word0 = self.words[word0_ind]
                word1 = self.words[word1_ind]
                edge_key = self.wordHash(word0, word1)
                if edge_key in self.structure:
                    edges.append((word0, word1, self.structure[edge_key]))

        return edges


    def wordHash(word0, word1):
        return "STRUCTURE__" + str((hash(word0) + hash(word1)) % sys.maxint)

