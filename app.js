angular.module('todoApp', [])
    .controller('TodoListController', function($scope, $http, $q) {

        var todoList = this;

        todoList.remaining = function() {
            var count = 0;
            angular.forEach(todoList.todos, function(todo) {
                count += todo.done ? 0 : 1;
            });
            return count;
        };

        todoList.getTodos = function getTodos() {
            $http({
                method: 'GET',
                url: 'http://localhost:9000/todo/api/v1.0/tasks',
                timeout: 1500
            }).then(function successCallback(response) {
                console.log(response);
                todoList.status = response.status +" "+ response.statusText;
                todoList.responseData = response.data;
                todoList.todos = []
                todoList.todos = response.data.tasks;
                todoList.lastUpdated = todoList.todos[todoList.todos.length-1].id;
                todoList.eventListener();

                // this callback will be called asynchronously
                // when the response is available
            }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
            });
        };

        todoList.postNewTodo = function postNewTodo() {
            $http({
                method: 'POST',
                url: 'http://localhost:9000/todo/api/v1.0/tasks',
                headers: {
                    'Content-Type': 'application/json'
                },
                data:todoList.newTodo,
                timeout: '1000'
            }).then(function successCallback(response) {
                console.log(response);
                todoList.status = response.status +" "+ response.statusText;
                todoList.responseData = response.data;
                todoList.todos.push(response.data.task);
                todoList.lastUpdated = response.data.task.id;
                // this callback will be called asynchronously
                // when the response is available
            }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
            });
        }

        todoList.eventListener = function eventListener(){ //add timeout here, add post in server, check for timestamp, return when found
           $http({
                method: 'POST',
                url: 'http://localhost:9000/todo/api/v1.0/tasks/notify',
                headers: {
                    'Content-Type': 'application/json'
                },
                data:{'id' : todoList.lastUpdated},
                timeout: '900000'
            }).then(function successCallback(response) {
                console.log(response);
                todoList.status = response.status +" "+ response.statusText;
                todoList.responseData = response.data;
                todoList.todos.push(response.data.task);
                todoList.lastUpdated = response.data.task.id;
                todoList.eventListener();
                // this callback will be called asynchronously
                // when the response is available
            }, function errorCallback(response) {
                todoList.eventListener();
                // called asynchronously if an error occurs
                // or server returns response with an error status.
            });
        }

        todoList.getTodos();

        todoList.addTodo = function() {
            todoList.newTodo = {
                'title': todoList.todoText,
                'done': false,
                'lastModified': new Date().getMilliseconds()
            }
            todoList.todoText = '';
            todoList.postNewTodo();
        };

    });
