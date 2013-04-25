from perlfunc import perlfunc, perlreq, perl5lib


@perlfunc
@perlreq('semantic_dist.pl')
def semantic_dist(word0, word1):
    pass


def WordRelations(wordlist):
    return {}, map(lambda k: {"NAME__":k}, wordlist)



if __name__ == "__main__":
    print semantic_dist('cat#n#1', 'dog#n#1')
