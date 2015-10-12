# What is it #

A demo web application in the spirit of [TodoMVC](http://todomvc.com/) showing how to use
**RethinkDB as a backend for Bottle and Ember.js applications**.

As any todo application, this one implements the following functionality:

* Managing database connections
* List existing todos
* Create new todo
* Retrieve a single todo
* Edit a todo or mark a todo as done
* Delete a todo

_Open issues_: when editing a todo, a `PUT` request is sent after each typed character. This could be improved to send a request is only once when Enter is pressed (pull requests welcome!)

# Complete stack #

* [Bottle](http://bottlepy.org/)
* [Ember (v1.0.0-pre.4-9-g6f709b0)](http://emberjs.com)
* [RethinkDB](http://www.rethinkdb.com)

# Installation #

```
git clone git://github.com/rethinkdb/rethinkdb-example-bottle-ember-todo.git
pip install bottle
pip install rethinkdb
```

_Note_: If you don't have RethinkDB installed, you can follow [these instructions to get it up and running](http://www.rethinkdb.com/docs/install/). 

# Running the application #

Firstly we'll need to create the database `todoapp` (you can override the name of the database
by setting the `TODO_DB` env variable) and the table used by this app: `todos`. You can
do this by running:

```
python todo.py --setup
```

Running the Bottle application is as simple as:

```
python todo.py
```

Then open a browser: <http://localhost:5000/>.


# License #

This demo application is licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
