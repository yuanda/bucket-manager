## flask modules
from flask import Flask
from flask import request, Response
from flask import render_template
from flask import make_response
from flask import g
from flask import redirect
from flask import session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import *
from flask.ext.security.datastore.sqlalchemy import SQLAlchemyUserDatastore

## python modules
from werkzeug import secure_filename
import json
import os
from random import choice

## local modules
from Neo4jInterface import *
from AuthInterface import *
from BucketStructure import *


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'VKqerq3E/adf23d0444'

AUTH_LEVEL = 4


def checkAuth():
    token = request.args.get('token')
    if not token:
        try:
            token = session['access_token']
        except KeyError:
            return redirect('http://data-dashboard.herokuapp.com')

    session['access_token'] = str(token)
    session['auth_level'] = getAccessLevel(session['access_token'])
    if session['auth_level'] < AUTH_LEVEL:
        return redirect('http://data-dashboard.herokuapp.com')

    updateSession(session['access_token'], session['auth_level'])


@app.route('/', methods=['POST', 'GET'])
def show_bucket():
##    checkAuth()

    bucket_list = getBuckets()

    if request.method == 'GET':
        if 'selected_bucket' in session and \
           session['selected_bucket'] in bucket_list:
            selected_bucket = session['selected_bucket']
            del session['selected_bucket']
            print 'out with the old!'
        else:
            selected_bucket = choice(bucket_list)
    else:
        selected_bucket = request.form['bucket_menu']

    bucket_data = loadBucket(selected_bucket)
    if bucket_data:
        keywords = bucket_data.getWords()
        edges = bucket_data.dumpEdges()
        centrality = bucket_data.dumpCentrality()
        bucket_stats = bucket_data.dumpStats()
    else:
        keywords = []
        edges = []
        centrality = []
        bucket_stats = {}

    bucket_stats.update({'SIZE__':len(keywords)})
    if not 'REACH__' in bucket_stats:
        bucket_stats['REACH__'] = 'unknown'

    return render_template('show_bucket.html', selected_bucket=bucket_stats, \
                                               bucket_list=bucket_list, \
                                               keywords=keywords, \
                                               keyword_centrality=centrality, \
                                               keyword_edges=edges \
                          )


@app.route('/save/', methods=['POST'])
def save_bucket():
##    checkAuth()

    bucket_name = request.form['new_bucket_name'].strip()
    tags = request.form['new_bucket_tags'].strip()
    keywords = request.form['new_bucket_contents'].strip()

    tags = map(lambda k: k.strip().lower(), tags.split(','))
    keywords = map(lambda k: k.strip(), keywords.split(','))

    new_bucket = BucketStructure(keywords)
    new_bucket.calculateEdges()
    saveBucket(bucket_name, tags, new_bucket)

    session['selected_bucket'] = bucket_name

    return redirect('/')


@app.route('/filter/', methods=['POST'])
def filter_bucket_list():
##    checkAuth()
    ## TODO implement this method
    return



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

