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
        selected_bucket = choice(bucket_list)

##    bucket_stats, bucket_contents = loadBucket(selected_bucket)

    bucket_contents = [{'NAME__':'science', 'CENTRALITY__':.1, 'sciences':.05, 'technology':.21}, \
                       {'NAME__':'sciences', 'CENTRALITY__':.11, 'science':.05, 'technology':.19}, \
                       {'NAME__':'technology', 'CENTRALITY__':.29, 'science':.21, 'sciences':.19}]
    bucket_stats = {'NAME__':'Science/Technology', 'REACH__':3511000, 'COHESION__':.87, 'SPREAD__':2.31, 'SIZE__':len(bucket_contents)}

##    return json.dumps([bucket_stats, bucket_contents])
    return render_template('show_bucket.html', selected_bucket=bucket_stats, bucket_list=bucket_list, bucket_contents=bucket_contents)


@app.route('/save/', methods=['POST'])
def save_bucket():
##    checkAuth()

    ## TODO: implement this method
    return



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

