// An example TodoMVC app created by
// [Tom Dale](http://github.com/tomdale) and
// [Addy Osmany](http://github.com/addyosmani)

// ember.js application

window.Todos = Ember.Application.create();

// ember.js routes
Todos.Router.map(function() {
  this.resource('todos', { path: '/' }, function() {
    this.route('active');
    this.route('completed');
  });
});

Todos.TodosRoute = Ember.Route.extend({
  model: function() {
    return Todos.Todo.find();
  }
});

Todos.TodosIndexRoute = Ember.Route.extend({
  setupController: function() {
    var todos = Todos.Todo.find();
    this.controllerFor('todos').set('filteredTodos', todos);
  }
});

Todos.TodosActiveRoute = Ember.Route.extend({
  setupController: function() {
    var todos = Todos.Todo.filter(function(todo) {
      if (!todo.get('isCompleted')) { return true; }
    });

    this.controllerFor('todos').set('filteredTodos', todos);
  }
});

Todos.TodosCompletedRoute = Ember.Route.extend({
  setupController: function() {
    var todos = Todos.Todo.filter(function(todo) {
      if (todo.get('isCompleted')) { return true; }
    });

    this.controllerFor('todos').set('filteredTodos', todos);
  }
});

// ember.js store: DS.RESTAdapter
Todos.Store = DS.Store.extend({
  revision: 11,
  adapter: 'DS.RESTAdapter'
});


// ember.js models
Todos.Todo = DS.Model.extend({
  title: DS.attr('string'),
  isCompleted: DS.attr('boolean'),

  todoDidChange: function() {
    Ember.run.once(this, function() {
      this.get('store').commit();
    });
  }.observes('isCompleted', 'title')
});

// ember.js controllers

Todos.TodosController = Ember.ArrayController.extend({
  createTodo: function() {
    // Get the todo title set by the "New Todo" text field
    var title = this.get('newTitle');
    if (!title.trim()) { return; }

    // Create the new Todo model
    Todos.Todo.createRecord({
      title: title,
      isCompleted: false
    });

    // Clear the "New Todo" text field
    this.set('newTitle', '');

    // Save the new model
    this.get('store').commit();
  },

  clearCompleted: function() {
    var completed = this.filterProperty('isCompleted', true);
    completed.invoke('deleteRecord');

    this.get('store').commit();
  },

  remaining: function() {
    return this.filterProperty( 'isCompleted', false ).get( 'length' );
  }.property( '@each.isCompleted' ),

  remainingFormatted: function() {
    var remaining = this.get('remaining');
    var plural = remaining === 1 ? 'item' : 'items';
    return '<strong>%@</strong> %@ left'.fmt(remaining, plural);
  }.property('remaining'),

  completed: function() {
    return this.filterProperty('isCompleted', true).get('length');
  }.property('@each.isCompleted'),

  hasCompleted: function() {
    return this.get('completed') > 0;
  }.property('completed'),

  allAreDone: function( key, value ) {
    if ( value !== undefined ) {
      this.setEach( 'isCompleted', value );
      return value;
    } else {
      return !!this.get( 'length' ) &&
        this.everyProperty( 'isCompleted', true );
    }
  }.property( '@each.isCompleted' )
});

Todos.TodoController = Ember.ObjectController.extend({
  isEditing: false,

  editTodo: function() {
    this.set('isEditing', true);
  },

  removeTodo: function() {
    var todo = this.get('model');

    todo.deleteRecord();
    todo.get('store').commit();
  }
});

// ember.js views

// todo view
Todos.TodoView = Ember.View.extend({
  tagName: 'li',
  classNameBindings: ['todo.isCompleted:completed', 'isEditing:editing'],

  doubleClick: function(event) {
    this.set('isEditing', true);
  }
});

// edit todo view
Todos.EditTodoView = Ember.TextField.extend({
  classNames: ['edit'],

  valueBinding: 'todo.title',

  change: function() {
    var value = this.get('value');

    if (Ember.isEmpty(value)) {
      this.get('controller').removeTodo();
    }
  },

  focusOut: function() {
    this.set('controller.isEditing', false);
  },

  insertNewline: function() {
    this.set('controller.isEditing', false);
  },

  didInsertElement: function() {
    this.$().focus();
  }
});
