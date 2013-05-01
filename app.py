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

    if not 'bucket_list' in session:
        bucket_list = getBuckets()
        session['bucket_list'] = bucket_list
    else:
        bucket_list = session['bucket_list']

    if not 'selected_bucket' in session or \
       not session['selected_bucket'] in bucket_list:
        selected_bucket = choice(bucket_list)
        session['selected_bucket'] = selected_bucket
    else:
        selected_bucket = session['selected_bucket']

    bucket_data = loadBucket(selected_bucket)
    keywords = bucket_data.getWords()
    edges = bucket_data.dumpEdges()
    centrality = bucket_data.dumpCentrality()

    bucket_stats = bucket_data.dumpStats()
    bucket_stats.update({'REACH__':'OVER 9000!', 'SIZE__':len(keywords)})

    return render_template('show_bucket.html', selected_bucket=bucket_stats, \
                                               bucket_list=bucket_list, \
                                               keywords=keywords, \
                                               keyword_centrality=centrality, \
                                               keyword_edges=edges \
                          )


@app.route('/save/', methods=['POST'])
def save_bucket():
##    checkAuth()

    print 'made it here'
    bucket_name = request.form['new_bucket_name']
    print 'and now here'
    tags = request.form['new_bucket_tags']
    print 'and now here too'
    keywords = request.form['new_bucket_contents']

    tags = map(lambda k: k.strip(), tags.split(','))
    keywords = map(lambda k: k.strip(), keywords.split(','))

    print bucket_name
    print tags
    print keywords

##    new_bucket = BucketStructure(keywords)
##    new_bucket.calculateEdges()
##    saveBucket(bucket_name, tags, new_bucket)
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

