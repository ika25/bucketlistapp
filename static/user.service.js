angular.module('bucketlistApp')
  .service('userService', [ '$resource', '$q',
    function userServiceFactory($resource, $q) {
      function formDataTransform (data) {
        var fd = new FormData();
        angular.forEach(data, function(value, key) {
          fd.append(key, value);
        });
        return fd;
      }
      function formUrlEncodedTransform(data) {
        var postData = [];
        for (var prop in data)
          postData.push(encodeURIComponent(prop) + "=" + encodeURIComponent(data[prop]));
        return postData.join("&");
      }
      function jsonTransformResponse(data, headersGetter, status) {
        try {
          return JSON.parse(data);
        } catch(e) {
          if(status == 200)
            throw e;
        }
        return data;
      }
      var API_PREFIX = 'api/';
      var userService = {
        myInfoCached: null,
        loginCheck: function() {
          var status;
          return userService.getMyInfo().then(function() {
            status = true;
          }).catch(function(response) {
            if(response.status == 403) {
              status = false;
              return;
            }
            throw response;
          }).then(function() {
            return status;
          });
        },
        getMyInfo: function() {
          if(userService.myInfoCached) {
            return $q.resolve(userService.myInfoCached);
          } else {
            return userService.me.get().$promise;
          }
        },
        me: $resource(API_PREFIX + 'myInfo', {}, {
          get: {
            method: 'GET',
            transformResponse: [ jsonTransformResponse, function(data) {
              if(data && data.status == 200) {
                userService.myInfoCached = data.record;
                return userService.myInfoCached;
              }
              return data;
            } ]
          },
          login: {
            method: 'POST',
            url: API_PREFIX + 'login',
            transformResponse: jsonTransformResponse,
            transformRequest: formUrlEncodedTransform,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
          },
          register: {
            method: 'POST',
            url: API_PREFIX + 'register',
            transformResponse: jsonTransformResponse,
            transformRequest: formUrlEncodedTransform,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
          },
          logout: {
            method: 'GET',
            url: API_PREFIX + 'logout',
            transformResponse: [ jsonTransformResponse, function(data) {
              if(data && data.status == 200) {
                userService.myInfoCached = null;
              }
              return data;
            } ]
          }
        }),
        todo: $resource(API_PREFIX + 'todo/:id', {}, {
          get: {
            method: 'GET',
            transformResponse: [ jsonTransformResponse, function(data) {
              if(data && data.status == 200)
                return data.record;
              return data;
            } ]
          },
          'delete': {
            method: 'DELETE',
            transformResponse: jsonTransformResponse
          },
          list: {
            method: 'GET',
            url: API_PREFIX + 'todos',
            transformResponse: jsonTransformResponse
          },
          create: {
            method: 'POST',
            url: API_PREFIX + 'todoCreate',
            transformResponse: jsonTransformResponse,
            transformRequest: formDataTransform,
            headers: {'Content-Type':undefined, enctype:'multipart/form-data'}
          },
          update: {
            method: 'POST',
            url: API_PREFIX + 'todoUpdate/:id',
            transformResponse: jsonTransformResponse,
            transformRequest: formDataTransform,
            headers: {'Content-Type':undefined, enctype:'multipart/form-data'},
            transformResponse: [ jsonTransformResponse, function(data) {
              if(data && data.status == 200)
                return data.record;
              return data;
            } ]
          },
        })
      };
      return userService;
    } ]);
