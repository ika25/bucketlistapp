angular.module('bucketlistApp')
  .component('dashboard', {
    templateUrl: 'dashboard.template.html',
    controller: [ 'gui', 'userService', '$location',
      function(gui, userService, $location) {
        var self = this;
        self.items = [];
        loadItems();
        self.onClickCheck = function(item) {
          self.loading = true;
          userService.todo.update({ id: item.id }, { checked: 1 }).$promise
            .then(function() { loadItems() }) // loadItems turns off loading
            .catch(gui.alerterrorbound);
        }
        self.onClickEdit = function(item) {
          $location.path('/todo/edit/' + item.id);
        }
        function loadItems() {
          self.loading = true;
          userService.todo.list({
            checked: 0,
            order_by: 'created_at desc',
            limit: 12
          }).$promise.then(function(data) {
            self.items = data.records;
          }).finally(function() { self.loading = false; })
            .catch(gui.alerterrorbound);
        }
      } ]
  });
