# A demo web application in the spirit of
# [TodoMVC](http://addyosmani.github.com/todomvc/) showing how to use
# **RethinkDB as a backend for Bottle and Ember.js applications**.
#
# For details about the complete stack, installation, and running the
# app see the
# [README](https://github.com/rethinkdb/rethinkdb-example-bottle-ember-todo).
import argparse
import json
import os
import socket

import bottle
from bottle import static_file, request

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

#### Connection details

# We will use these settings later in the code to connect to the
# RethinkDB server.
RDB_HOST =  os.getenv('RDB_HOST', 'localhost')
RDB_PORT = os.getenv('RDB_PORT', 28015)
TODO_DB = os.getenv('TODO_DB', 'todoapp')

#### Setting up the app database

# The app will use a table `todos` in the database specified by the
# `TODO_DB` variable (defaults to `todoapp`).  We'll create the database and table here using
# [`db_create`](http://www.rethinkdb.com/api/#py:manipulating_databases-db_create)
# and
# [`table_create`](http://www.rethinkdb.com/api/#py:manipulating_tables-table_create) commands.
def dbSetup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(TODO_DB).run(connection)
        r.db(TODO_DB).table_create('todos').run(connection)
        print 'Database setup completed. Now run the app without --setup: `python todo.py`'
    except RqlRuntimeError:
        print 'App database already exists. Run the app without --setup: `python todo.py`'
    finally:
        connection.close()


#### Managing connections

# The pattern we're using for managing database connections is to have **a connection per request**. 
# We're using Bottle's `@bottle.hook('before_request')` and `@bottle.hook('after_request')` for 
# [opening a database connection](http://www.rethinkdb.com/api/#py:accessing_rql-connect) and 
# [closing it](http://www.rethinkdb.com/api/#py:accessing_rql-close) respectively.

@bottle.hook('before_request')
def before_request():
    if request.path.startswith('/static/'):
        return
    try:
        bottle.local.rdb_connection  = r.connect(RDB_HOST, RDB_PORT, TODO_DB)
    except RqlDriverError:
        bottle.abort(503, "No database connection could be established.")

@bottle.hook('after_request')
def after_request():
    if request.path.startswith('/static/'):
        return
    bottle.local.rdb_connection.close()

#### Listing existing todos

# To retrieve all existing tasks, we are using
# [`r.table`](http://www.rethinkdb.com/api/#py:selecting_data-table)
# command to query the database in response to a GET request from the
# browser. When `table(table_name)` isn't followed by an additional
# command, it returns all documents in the table.
#    
# Running the query returns an iterator that automatically streams
# data from the server in efficient batches.
@bottle.get("/todos")
def get_todos():
    selection = list(r.table('todos').run(bottle.local.rdb_connection))
    return json.dumps({'todos': selection})

#### Creating a todo

# We will create a new todo in response to a POST request to `/todos`
# with a JSON payload using
# [`table.insert`](http://www.rethinkdb.com/api/#py:writing_data-insert).
#
# The `insert` operation returns a single object specifying the number
# of successfully created objects and their corresponding IDs:
# `{ "inserted": 1, "errors": 0, "generated_keys": ["773666ac-841a-44dc-97b7-b6f3931e9b9f"] }`
@bottle.post("/todos")
def new_todo():
    todo = request.json['todo']
    inserted = r.table('todos').insert(todo).run(bottle.local.rdb_connection)
    todo['id'] = inserted['generated_keys'][0]
    return json.dumps({'todo': todo})


#### Retrieving a single todo

# Every new task gets assigned a unique ID. The browser can retrieve
# a specific task by GETing `/todos/<todo_id>`. To query the database
# for a single document by its ID, we use the
# [`get`](http://www.rethinkdb.com/api/#py:selecting_data-get)
# command.
#
# Using a task's ID will prove more useful when we decide to update
# it, mark it completed, or delete it.
@bottle.get("/todos/<todo_id>")
def get_todo(todo_id):
    todo = r.table('todos').get(todo_id).run(bottle.local.rdb_connection)
    return json.dumps({'todo': todo})

#### Editing/Updating a task

# Updating a todo (editing it or marking it completed) is performed on
# a `PUT` request.  To save the updated todo we'll do a
# [`replace`](http://www.rethinkdb.com/api/#py:writing_data-replace).
@bottle.put("/todos/<todo_id>")
def update_todo(todo_id):
    todo = {'id': todo_id}
    todo.update(request.json['todo'])
    return json.dumps(r.table('todos').get(todo_id).replace(todo).run(bottle.local.rdb_connection))

# If you'd like the update operation to happen as the result of a
# `PATCH` request (carrying only the updated fields), you can use the
# [`update`](http://www.rethinkdb.com/api/#py:writing_data-update)
# command, which will merge the JSON object stored in the database
# with the new one.
@bottle.route("/todos/<todo_id>", method='PATCH')
def patch_todo(todo_id):
    return json.dumps(r.table('todos').get(todo_id).update(request.json['todo']).run(bottle.local.rdb_connection))


#### Deleting a task

# To delete a todo item we'll call a
# [`delete`](http://www.rethinkdb.com/api/#py:writing_data-delete)
# command on a `DELETE /todos/<todo_id>` request.
@bottle.delete("/todos/<todo_id>")
def delete_todo(todo_id):
    return json.dumps(r.table('todos').get(todo_id).delete().run(bottle.local.rdb_connection))

@bottle.get("/")
def show_todos():
    return static_file('todo.html', root='templates/', mimetype='text/html')

@bottle.route('/static/<filename:path>', method='GET')
@bottle.route('/static/<filename:path>', method='HEAD')
def send_static(filename):
    return static_file(filename, root='static/')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Bottle todo app')
    parser.add_argument('--setup', dest='run_setup', action='store_true')

    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    else:
        bottle.run(host='localhost', port=5000, debug=True, reloader=True)


# ### Best practices ###
#
# #### Managing connections: a connection per request ####
#
# The RethinkDB server doesn't use a thread-per-connnection approach
# so opening connections per request will not slow down your database.
# 
# #### Fetching multiple rows: batched iterators ####
#
# When fetching multiple rows from a table, RethinkDB returns a
# batched iterator initially containing a subset of the complete
# result. Once the end of the current batch is reached, a new batch is
# automatically retrieved from the server. From a coding point of view
# this is transparent:
#   
#     for result in r.table('todos').run(connection):
#         print result
#     
#    
# #### `replace` vs `update` ####
#
# Both `replace` and `update` operations can be used to modify one or
# multiple rows. Their behavior is different:
#    
# *   `replace` will completely replace the existing rows with new values
# *   `update` will merge existing rows with the new values


#
# Licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
#
# Copyright (c) 2012 RethinkDB
#
