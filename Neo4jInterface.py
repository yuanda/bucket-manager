## python modules
from py2neo import neo4j, cypher
import re

## local modules
from WordRelations import *
from BucketStructure import *


## error handler for cypher queries
## should probably do something with this
def errorHandler(e):
    print type(e), e.message


## connects to the neo4j database and returns a handle
def getDBhandle():
    db = None
    while not (type(db) == neo4j.GraphDatabaseService):
        try:
            db = neo4j.GraphDatabaseService("http://ec2-107-22-155-191.compute-1.amazonaws.com:7474/db/data/")
        except Exception as e:
            print type(e), e.message
    return db


## keeps trying to connect until it can
def submit_query(db, query, error_handler=errorHandler):
    print query
    while True:
        try:
            return cypher.execute(db, query, error_handler=errorHandler)
        except Exception as e:
            print type(e), e.message


## returns a BucketStructure object for the given bucket name
def loadBucket(bucket_name):
    db = getDBhandle()

    query = 'START b=node:buckets("bucket:' + re.sub('[^A-z0-9]', '?', bucket_name) + '") ' \
          + 'WHERE has(b.NAME__) ' \
          + 'RETURN b;' \

    bucket, metadata = submit_query(db, query)
    if bucket:
        bucket = bucket[0][0]
        bucket_structure = BucketStructure()
        bucket_structure.loadStructure(bucket.get_properties())
    else:
        print 'no bucket!'

    return bucket_structure


## saves a bucket with the given name, tags, and structure
## where tags are given as a str list and
## bucket_structure is given as a BucketStructure object
def saveBucket(bucket_name, tags, bucket_structure):
    db = getDBhandle()

    ## finds or creates unconnected bucket node
    bucket_index = db.get_or_create_index(neo4j.Node, "buckets")
    bucket_contents = bucket_structure.dumpStructure()
    bucket_contents.update({'NAME__':bucket_name, 'TAGS__':', '.join(tags)})
    bucket_root = bucket_index.get_or_create("bucket", bucket_name, bucket_contents)
    bucket_root.isolate()

    ## finds or creates tag nodes, connecting to bucket node
    tag_index = db.get_or_create_index(neo4j.Node, "tags")
    for tag in tags:
        tag_node = tag_index.get_or_create("tag", tag, {'NAME__':tag})
        tag_node.create_path("TAGS", bucket_root)

    ## finds or creates word nodes, connecting to bucket node
    word_index = db.get_or_create_index(neo4j.Node, "words")
    for bucket_word in bucket_structure.getWords():
        word_node = bucket_index.get_or_create("word", bucket_word, {'NAME__':bucket_word})
        bucket_root.create_path("CONTAINS", word_node)


## returns a list of all bucket names
## filters to include only buckets with
## all given tags iff tags != None
def getBuckets(tags=[]):
    db = getDBhandle()

    bucket_names = set([])

    ## filtered list
    if tags:
        bucket_names = set([])

        for tag in tags:
            query = 'START t=node:tags("tag:' + tag + '") ' \
                  + 'MATCH t-[:TAGS]->b ' \
                  + 'WHERE has(b.NAME__) ' \
                  + 'RETURN b.NAME__;'
            tmp_names, metadata = submit_query(db, query)
            tmp_names = map(lambda k: str(k[0]), tmp_names)

            if bucket_names:
                bucket_names = bucket_names & tmp_names
            else:
                bucket_names = tmp_names
            tmp_names = set([])

        bucket_names = list(bucket_names)

    ## all buckets
    else:
        bucket_names = []
        query = 'START b=node:buckets("bucket:*") WHERE has(b.NAME__) return b.NAME__'
        bucket_names, metadata = submit_query(db, query)
        bucket_names = map(lambda k: str(k[0]), bucket_names)

    bucket_names.sort()
    return bucket_names



if __name__ == "__main__":
    from sys import *

##    db = getDBhandle()

##    if len(argv) > 1:
##        bucket_name = ' '.join(argv[1:])
##        print bucket_name
##        print loadBucket(bucket_name)

##    print getBuckets()


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
    saveBucket('Pets (Cats)', ['Animals', 'Pets'], x)

