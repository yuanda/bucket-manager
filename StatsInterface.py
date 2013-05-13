## python modules
from threading import *
from storm.locals import *
from time import sleep


def getDBhandle():
    dbname = 'postgres://fifmkeftvutysz:gUuDxC3K9LhKB2koOCLVpIit7e@ec2-54-235-155-182.compute-1.amazonaws.com:5432/d41qkgihdppdi4'

    store = None
    while not store:
        try:
            database = create_database(dbname)
            store = Store(database)
        except Exception as e:
            print '[ Error getting stats DB handle ]', type(e), e.message
            sleep(.25)

    return store


def make_query(db, query):
    while True:
        try:
            results = db.execute(query)
            results = results.get_all()
            return results
        except Exception as e:
            print '[', 'Error on query', query, ']', type(e), e.message
            sleep(.25)


class StatsFetcher:

    def __init__(self, bucket_key, stats):
        self.bucket_key = bucket_key
        self.stats = stats

        self.data = {}
        self.workers = []

        if bucket_key and stats:
            self.db = getDBhandle()
    
            for stat in self.stats:
                new_worker = StatThread(stat, self.bucket_key, self.db, self.data)
                self.workers.append(new_worker)
                new_worker.start()


    def getStats(self):
        map(lambda k: k.join(), self.workers)
        self.workers = []
        return self.data



class StatThread(Thread):

    def __init__(self, stat, bucket_key, db, data):
        Thread.__init__(self)

        self.stat = stat
        self.bucket_key = bucket_key
        self.db = db
        self.data = data


    def run(self):
        result = None

        if self.stat == 'CTR':
            query = 'SELECT SUM(clicks)/SUM(impressions) ' \
                  + 'FROM bucket_stats ' \
                  + 'WHERE keywords_hash = \'' + self.bucket_key + '\';'
            result = make_query(self.db, query)

        elif self.stat == 'CPC':
            query = 'SELECT SUM(spent)/SUM(clicks) ' \
                  + 'FROM bucket_stats ' \
                  + 'WHERE keywords_hash = \'' + self.bucket_key + '\';'
            result = make_query(self.db, query)

        elif self.stat == 'CPM':
            query = 'SELECT 1000*SUM(spent)/SUM(impressions) ' \
                  + 'FROM bucket_stats ' \
                  + 'WHERE keywords_hash = \'' + self.bucket_key + '\';'
            result = make_query(self.db, query)

        if result and result[0] and result[0][0]:
            self.data[self.stat] = result[0][0]
       

if __name__ == "__main__":
    ## no bucket key
##    x = StatsFetcher(None, ['CPC', 'CPM', 'CTR'])

    ## bad bucket key
##    x = StatsFetcher('lafjoi09', ['CPC', 'CPM', 'CTR'])

    ## good bucket key
    x = StatsFetcher('00ab36ed3cc11a108184fa7a71f94215', ['CPC', 'CPM', 'CTR']) 

    print x.getStats()
