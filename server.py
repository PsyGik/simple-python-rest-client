#!virtual/bin/python
import flask
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request

import json

import flask
import httplib2
from apiclient import discovery
from oauth2client import client

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import time

from peewee import *
from playhouse.shortcuts import model_to_dict
from flask import g
import logging
import logging.config

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='myapp.log',
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


app = Flask(__name__)
tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False,
        'lastModified': 0
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False,
        'lastModified': 0
    }
]

returnData = []
count = 0

db = SqliteDatabase('tasks.db')


class Task(Model):
    title = CharField()
    done = BooleanField()
    lastModified = DateField()

    class Meta:
        database = db


def init_db():
    db.connect()
    Task.create_table()
    Task.create(title="Task 1", done=False, lastModified=time.time())
    Task.create(title="Task 2", done=False, lastModified=time.time())
    Task.create(title="Task 3", done=False, lastModified=time.time())
    Task.create(title="Task 4", done=False, lastModified=time.time())
    Task.create(title="Task 5", done=False, lastModified=time.time())
    Task.create(title="Task 6", done=False, lastModified=time.time())
    db.close()


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@crossdomain(origin='*')
def get_tasks():
    print "Getting Tasks"
    query = []
    for task in Task.select():
        query.append(model_to_dict(task))
    return jsonify({'tasks': query})


@app.errorhandler(404)
@crossdomain(origin='*')
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@crossdomain(origin='*')
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def create_task():
    print "Inserting Task"
    if not request.json or not 'title' in request.json:
        abort(400)
    task = Task.create(title=request.json['title'], done=False, lastModified=request.json.get('lastModified', ""))
    print "Saving", model_to_dict(task)
    return jsonify({'task': model_to_dict(task)}), 201


@app.route('/todo/api/v1.0/tasks/notify', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def notify_task():
    # print "Listening for Notification", request.json.get('id', 0)
    if not request.json or not 'id' in request.json:
        abort(400)
    last_item_id = request.json.get('id', 0)
    query = {}
    while len(query) <= 0:
        time.sleep(5)
        try:
            task = Task.get(Task.id > last_item_id)
            query = model_to_dict(task)
            print "query", query
            return jsonify({'task': query}), 201
        except Task.DoesNotExist as err:
            print err


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*')
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE', 'OPTIONS'])
@crossdomain(origin='*')
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    import uuid

    app.secret_key = str(uuid.uuid4())
    app.run(port=9000, debug=True, threaded=True)
    # init_db()
