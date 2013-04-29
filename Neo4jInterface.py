## python modules
from py2neo import neo4j, cypher
import re

## local modules
from WordRelations import *


## error handler for cypher queries
## should probably do something with this
def errorHandler(e):
    pass


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
def submit_query(db, query, row_handler=None):
    print query
    while True:
        try:
            cypher.execute(db, query, row_handler=row_handler, error_handler=errorHandler)
            return
        except Exception as e:
            print type(e), e.message


## returns a BucketStructure object for the given bucket name
def loadBucket(bucket_name):
    db = getDBhandle()

    bucket = []
    def bucket_stat_handler(row):
        bucket_structure = BucketStructure()
        bucket_structure.loadStructure(row[0].get_properties())
        bucket.append(bucket_structure)

    query = 'START b=node:buckets("bucket:' + re.sub('[ ()]', '?', bucket_name) + '") ' \
          + 'WHERE has(b.NAME__) ' \
          + 'RETURN b' \

    submit_query(db, query, row_handler=bucket_stat_handler)
    bucket = bucket[0]

    return bucket


## saves a bucket with the given name, tags, and structure
## where tags are given as a str list and
## bucket_structure is given as a BucketStructure object
def saveBucket(bucket_name, tags, bucket_structure):
    db = getDBhandle()

    ## finds or creates unconnected bucket node
    bucket_index = db.get_or_create_index(neo4j.Node, "buckets")
    bucket_root = bucket_index.get_or_create("bucket", bucket_name, bucket_structure.dumpStructure())
    bucket_root.isolate()

    ## finds or creates tag nodes, connecting to bucket node
    tag_index = db.get_or_create(neo4j.Node, "tags")
    for tag in tags:
        tag_node = tag_index.get_or_create("tag", tag, {})
        tag_node.create_path("TAGS", bucket_root)

    ## finds or creates word nodes, connecting to bucket node
    word_index = db.get_or_create_index(neo4j.Node, "words")
    for bucket_word in bucket_structure.getWords():
        word_node = bucket_index.get_or_create("word", bucket_word, {})
        bucket_root.create_path("CONTAINS", word_node)


## returns a list of all bucket names
## filters to include only buckets with
## all given tags iff tags != None
def getBuckets(tags=[]):
    db = getDBhandle()

    bucket_names = set([])
    def row_handler(row):
        bucket_names.add(str(row[0]))

    ## filtered list
    if tags:
        tmp_names = set([])
        bucket_names = set([])
        def row_handler(row):
            tmp_names.add(str(row[0]))

        for tag in tags:
            query = 'START t=node:tags("tag:' + tag + '") ' \
                  + 'MATCH t-[:TAGS]->b ' \
                  + 'RETURN b.NAME__;'
            submit_query(db, query, row_handler=row_handler)

            if bucket_names:
                bucket_names = bucket_names & tmp_names
            else:
                bucket_names = tmp_names
            tmp_names = set([])

        bucket_names = list(bucket_names)

    ## all buckets
    else:
        bucket_names = []
        def row_handler(row):
            bucket_names.append(str(row[0]))
        query = 'START b=node:buckets("bucket:*") where has(b.name) return b.name'
        submit_query(db, query, row_handler=row_handler)

    bucket_names.sort()
    return bucket_names



if __name__ == "__main__":
    from sys import *

##    db = getDBhandle()

    if len(argv) > 1:
        bucket_name = ' '.join(argv[1:])
        print bucket_name
        print loadBucket(bucket_name)

##    print getBuckets()
