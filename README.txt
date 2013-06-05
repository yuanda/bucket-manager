stores, manages, and displays Adaptly's Facebook keyword buckets

AuthInterface.py
    functions for interacting with the dashboard authentication API

BucketStructure.py
    class for holding a bucket's contents as well as calculating
    keyword relatedness using WordRelations.py

Neo4jInterface.py
    functions for interacting with the neo4j database that holds
    bucket structure data for the bucket manager

StatsInterface.py
    classes (StatsFetcher, StatThread) for interacting with the 
    bucket stats postgresql database

WordRelations.py
    functions for finding semantic relations between keyword phrases
