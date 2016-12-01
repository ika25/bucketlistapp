angular.module('bucketlistApp')
  .component('todoEdit', {
    templateUrl: 'todo-edit.template.html',
    controller: [ '$scope', 'gui', 'userService', '$location', '$route',
      function($scope, gui, userService, $location, $route) {
        function transformTodoItem(item) {
          item.checked = item.checked ? true : false;
          return item;
        }
        var self = this;
        var todoId = $route.current.params.todoId;
        var imageHasSetToUndefined = false;
        if(!todoId) {
          // new
          self.todo = {
            title: '',
            checked: false,
            image: null,
            description: ''
          };
        } else {
          // edit
          self.todo = null;
          userService.todo.get({ id: todoId }).$promise
            .then(function(record) {
              self.todo = transformTodoItem(record);
              setTimeout(function() {
                // needs delay because ng-if for todo is setup on
                // parent element
                $scope.$apply(function() {
                  self.onImageRevert();
                });
              }, 10);
            }).catch(gui.alerterrorbound);
        }
        self.onImageRevert = function() {
          var input = $('.imageupload input[type=file]')[0];
          imageHasSetToUndefined = true;
          if(input) {
            input.value = null;
            $(input).trigger('change');
          }
          var img = $('.imageupload .fileinput-new.thumbnail img')[0];
          if(img) {
            if(self.todo.image) {
              img.src = self.todo.image;
            } else {
              img.src = "";
            }
          }
          self.todo.upload_image = 'undefined';
        }
        self.onImageRemoveClick = function() {
          self.todo.upload_image = null;
          var input = $('.imageupload input[type=file]')[0];
          if(input) {
            input.value = null;
            $(input).trigger('change');
          }
          var img = $('.imageupload .fileinput-new.thumbnail img')[0];
          if(img) {
            img.src = "";
          }
        }
        self.onImageChange = function(input) {
          if(imageHasSetToUndefined) {
            imageHasSetToUndefined = false;
            return;
          }
          setTimeout(function() {
            $scope.$apply(function() {
              if(input.files.length > 0) {
                self.todo.upload_image = input.files[0];
              } else {
                self.todo.upload_image = null;
              }
            });
          }, 1);
        }
        self.onSave = function() {
          var todo = self.todo,
              todoId = todo.id;
          todo = {
            title: todo.title,
            description: todo.description,
            checked: todo.checked ? 1 : 0
          };
          if(self.todo.upload_image !== 'undefined') {
            if(self.todo.upload_image) {
              todo.image = self.todo.upload_image;
            } else if(todoId) {
              todo.image = '';
            }
          }
          var promise;
          if(todoId) {
            promise = userService.todo.update({id:todoId}, todo).$promise;
          } else {
            promise = userService.todo.create(todo).$promise;
          }
          gui.blockloading();
          promise
            .then(function() {
              history.back();
              // $location.path('/todo/manage');
            })
            .finally(gui.unblockbound)
            .catch(gui.alerterrorbound);
        };
      } ]
  });
