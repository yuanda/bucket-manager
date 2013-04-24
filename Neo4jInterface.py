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


def loadBucket(bucket_name):
    db = getDBhandle()

    ## bucket info

    bucket_stats = []
    def bucket_stat_handler(row):
        bucket_stats.append(row[0].get_properties())

    query = 'START n=node:buckets("bucket:' + re.sub('[ ()]', '?', bucket_name) + '") ' \
          + 'WHERE has(n.name) ' \
          + 'RETURN n' \

    submit_query(db, query, row_handler=bucket_stat_handler)
    bucket_stats = bucket_stats[0]

    ## keyword info

    bucket_contents = []
    def keyword_handler(row):
        bucket_contents.append(row[0].get_properties())

    query = 'START n=node:buckets("bucket:' + re.sub('[ ()]', '?', bucket_name) + '") ' \
          + 'MATCH n-->w ' \
          + 'WHERE has(w.name) ' \
          + 'RETURN w'

    submit_query(db, query, row_handler=keyword_handler)

    return bucket_stats, bucket_contents


def saveBucket(bucket_name, bucket_contents):
    db = getDBhandle()

    bucket_index = db.get_or_create_index(neo4j.Node, "buckets")
    bucket_root = bucket_index.get_or_create("bucket", bucket_name, {"name": bucket_name})
    bucket_root.isolate()

    word_index = db.get_or_create_index(neo4j.Node, "words")
    for bucket_word in bucket_contents:
        word_node = bucket_index.get_or_create("word", bucket_word["name"], bucket_word)
        bucket_root.create_path("CONTAINS", word_node)


def getBuckets():
    db = getDBhandle()

    bucket_names = []
    def row_handler(row):
        bucket_names.append(str(row[0]))

    query = 'START n=node:buckets("bucket:*") where has(n.name) return n.name'
    submit_query(db, query, row_handler=row_handler)

    bucket_names.sort()
    return bucket_names


def deleteBucket(bucket_name):
    db = getDBhandle()

    bucket_index = db.get_or_create_index(neo4j.Node, "buckets")
    bucket_root = bucket_index.get_or_create("bucket", bucket_name, {"name": bucket_name})
    bucket_root.isolate()
    bucket_root.delete()


if __name__ == "__main__":
    from sys import *

##    db = getDBhandle()

    if len(argv) > 1:
        bucket_name = ' '.join(argv[1:])
        print bucket_name
        print loadBucket(bucket_name)
    else:
        saveBucket("colors", [{"name":"red"}, {"name":"blue"}, {"name":"yellow"}, {"name":"green"}])
        print loadBucket("colors")

##    print getBuckets()
