## python modules
from py2neo import neo4j, cypher
import re

## local modules
from WordRelations import *
from BucketStructure import *


SEMANTIC_WEB_URL = 'http://ec2-54-234-151-173.compute-1.amazonaws.com:7474/db/data'
BUCKET_MANAGER_URL = 'http://ec2-54-226-2-179.compute-1.amazonaws.com:7474/db/data/'


## error handler for cypher queries
## should probably do something with this
def errorHandler(e):
    print type(e), e.message


## connects to the neo4j database and returns a handle
def getDBhandle(isSemanticWeb=False):
    db = None
    if isSemanticWeb:
        db_url = SEMANTIC_WEB_URL
    else:
        db_url = BUCKET_MANAGER_URL

    while not (type(db) == neo4j.GraphDatabaseService):
        try:
            db = neo4j.GraphDatabaseService(db_url)
        except Exception as e:
            print type(e)
    return db


## keeps trying to connect until it can
def submit_query(db, query, error_handler=errorHandler):
    print query
    while True:
        try:
            return cypher.execute(db, query, error_handler=errorHandler)
        except TypeError:
            return None
        except Exception as e:
            print type(e)


def shortestPath(topic0, topic1):
    db = getDBhandle(isSemanticWeb=True)

    query = 'START m=node:topics(TOPIC=\'' + topic0 + '\'), ' \
                + 'n=node:topics(TOPIC=\'' + topic1 + '\') ' \
          + 'MATCH p=shortestPath(m-[*]-n) ' \
          + 'RETURN LENGTH(p);'

    topic_dist = submit_query(db, query)
    return topic_dist 


## returns a BucketStructure object for the given bucket name
def loadBucket(bucket_name):
    db = getDBhandle()

    query = 'START b=node:buckets("bucket:' + re.sub('[^A-z0-9]', '?', bucket_name) + '") ' \
          + 'WHERE has(b.NAME__) ' \
          + 'RETURN b;' \

    results = submit_query(db, query)
    if results:
        bucket, metadata = results
        bucket = bucket[0][0]
        bucket_structure = BucketStructure()
        bucket_structure.loadStructure(bucket.get_properties())
    else:
        print 'no bucket!'
        return None

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
            tmp_names = set(map(lambda k: str(k[0]), tmp_names))

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
        results = submit_query(db, query)
        if not results:
            return bucket_names

        bucket_names, metadata = results
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
                                  "#CPU cache", \
                                  "#Computer", \
                                  "#Computer architecture", \
                                  "#Computer data storage", \
                                  "#Computer file", \
                                  "#Computer network", \
                                  "#Computer programming", \
                                  "#Computer science", \
                                  "#Computers", \
                                  "#Data analysis", \
                                  "#Engineering", \
                                  "#Information technology", \
                                  "#Internet", \
                                  "#Java (programming language)", \
                                  "#Java (software platform)", \
                                  "#Laptop", \
                                  "#Personal computer", \
                                  "#Python (programming language)", \
                                  "#Ruby (programming language)", \
                                  "#Technology", \
                                  "#Website", \
                                  "#World Wide Web"
                              ])
    x.calculateEdges()
    saveBucket('Computer Science', ['Technology', 'Internet'], x)

