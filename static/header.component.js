angular.module('bucketlistApp')
  .component('header', {
    templateUrl: 'header.template.html',
    controller: [ '$rootScope', 'gui', 'userService', '$location', '$route', 
      function($rootScope, gui, userService, $location, $route) {
        var self =this;
        self.origPath = $route.current.originalPath;
        self.onLogoutClick = function(event) {
          event.preventDefault();
          gui.blockloading();
          userService.me.logout().$promise
            .then(function() { $location.path('/login'); })
            .finally(gui.unblockbound)
            .catch(gui.alerterrorbound);
        }
        $rootScope.$on('$locationChangeSuccess', function() {
          var currentRoute = $route.current,
              origPath = currentRoute ? currentRoute.originalPath : '';
          self.origPath = origPath;
        })
      } ]
  });
