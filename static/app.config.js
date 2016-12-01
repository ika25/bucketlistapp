'use strict';
var httpRequestDelay = 850;
angular.module('bucketlistApp')
  .config(['$locationProvider', '$routeProvider',
    function config($locationProvider, $routeProvider) {
      function mkIsLoggedIn(forLogin) {
        return ["userService", "gui", "$location",
          function(userService, gui, $location) {
            return userService.loginCheck().then(function(success) {
              if(forLogin) {
                if(success) {
                  $location.path('/dashboard');
                }
              } else {
                if(!success) {
                  $location.path('/login');
                }
              }
              return success;
            }).catch(gui.alerterrorbound);
          } ];
      }
      $locationProvider.html5Mode(true);
      function userPageOpt(opts) {
        var data = opts.data = opts.data || {};
        data.userPage = true;
        var resolve = opts.resolve = opts.resolve || {};
        resolve.isLoggedIn = mkIsLoggedIn();
        return opts;
      }
      $routeProvider
        .when('/login', {
          template: '<login></login>',
          resolve: {
            isLoggedIn: mkIsLoggedIn(true)
          }
        })
        .when('/', { redirectTo: '/dashboard' })
        .when('/dashboard', userPageOpt({
          template: '<dashboard></dashboard>'
        }))
        .when('/todo', { redirectTo: '/todo/manage' })
        .when('/todo/manage', userPageOpt({
          template: '<todo-manage></todo-manage>'
        }))
        .when('/todo/manage/:itemsScroll', userPageOpt({
          template: '<todo-manage></todo-manage>'
        }))
        .when('/todo/new', userPageOpt({
          template: '<todo-edit></todo-edit>'
        }))
        .when('/todo/edit/:todoId', userPageOpt({
          template: '<todo-edit></todo-edit>'
        }))
        .when('/defer', { template: '' });
    }])
  .config([ '$httpProvider',
    function simulateNetworkLatency( $httpProvider ) {
      if(httpRequestDelay <= 0)
        return;
      $httpProvider.interceptors.push( httpDelay );
      // I add a delay to both successful and failed responses.
      function httpDelay( $timeout, $q ) {
        // Return our interceptor configuration.
        return({
          response: response,
          responseError: responseError
        });
        // ---
        // PUBLIC METHODS.
        // ---
        // I intercept successful responses.
        function response( response ) {
          var deferred = $q.defer();
          $timeout(
            function() { deferred.resolve( response ); }, httpRequestDelay,
            // There's no need to trigger a $digest - the view-model has
            // not been changed.
            false
          );
          return( deferred.promise );
        }
        // I intercept error responses.
        function responseError( response ) {
          var deferred = $q.defer();
          $timeout(
            function() { deferred.reject( response ); }, httpRequestDelay,
            // There's no need to trigger a $digest - the view-model has
            // not been changed.
            false
          );
          return( deferred.promise );
        }
      }
    } ]);
