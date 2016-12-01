angular.module('bucketlistApp')
  .component('login', {
    templateUrl: 'login.template.html',
    controller: [ 'gui', 'userService', '$location',
      function(gui, userService, $location) {
        var self = this;
        self.register = {
          username: '',
          password: '',
          first_name: '',
          last_name: '',
          email: ''
        };
        self.username = '';
        self.password = '';
        self.loginSubmit = function() {
          gui.blockloading()
          userService.me.login({
            username: self.username,
            password: self.password
          }).$promise
            .then(function() { return userService.getMyInfo() })
            .then(function(mInfo) { $location.path('/dashboard') })
            .finally(gui.unblockbound)
            .catch(gui.alerterrorbound);
        }
        self.registerSubmit = function() {
          gui.blockloading()
          userService.me.register(self.register).$promise
            .then(function() {
              return userService.me.login({
                username: self.register.username,
                password: self.register.password
              }).$promise
            })
            .then(function() { return userService.getMyInfo() })
            .then(function(mInfo) { $location.path('/dashboard') })
            .finally(gui.unblockbound)
            .catch(gui.alerterrorbound);
        }
      } ]
  });
