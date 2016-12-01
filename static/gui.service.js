angular.module('bucketlistApp')
  .service('gui', [ '$q',
    function guiFactory($q) {
      var gui = {
        mpopupPromise: $q.resolve(),
        applyInScopeAsync: function(func) {
          var $scope = this.$scope;
          setTimeout(function() {
            $scope.$apply(func);
          }, 1);
        },
        alerterror: function(reason) {
          if(typeof(reason) == 'object' && reason.status) {
            if(reason.status == -1)
              return $q.resolve();
            if(typeof(reason.data) == 'object') {
              reason = reason.data.status + ': ' +
                reason.data.error_message;
            } else {
              reason = reason.status + ': ' + reason.statusText;
            }
          }
          return this.alert('Error', reason);
        },
        alert: function(title, body) {
          var $scope = this.$scope;
          var self = this;
          if(!$scope)
            return $q.resolve();
          return this.mpopupPromise = this.mpopupPromise.then(() => {
            return $q(function(resolve) {
              self.applyInScopeAsync(function() {
                var mpopup = $scope.mainpopup;
                mpopup.title = title;
                mpopup.body = body;
                mpopup.buttons = [];
                mpopup.hasclose = true;
                mpopup.closelabel = "Close";
                mpopup.popup().then(resolve)
              });
            })
          });
        },
        confirm: function(title, body, btntype) {
          var $scope = this.$scope;
          var self = this;
          if(!$scope)
            return $q.resolve();
          return this.mpopupPromise = this.mpopupPromise.then(() => {
            return $q(function(resolve) {
              self.applyInScopeAsync(function() {
                var mpopup = $scope.mainpopup;
                var resolveStatus = false;
                mpopup.title = title;
                mpopup.body = body;
                mpopup.buttons = [
                  {
                    label: 'Yes',
                    btntype: btntype ? btntype : 'primary',
                    onClick: function() {
                      resolveStatus = true;
                      mpopup.close()
                    }
                  },
                  {
                    label: 'No',
                    btntype: 'default',
                    onClick: function() {
                      resolveStatus = false;
                      mpopup.close();
                    }
                  }
                ];
                mpopup.hasclose = false;
                mpopup.popup().then(function() {
                  resolve(resolveStatus);
                })
              });
            })
          });
        },
        isblocking: function() {
          var $scope = this.$scope;
          if(!$scope)
            return;
          return $scope.processblocker.isBlocking();
        },
        blockloading: function() {
          return this.block("Loading...")
        },
        block: function(message) {
          var $scope = this.$scope;
          if(!$scope)
            return;
          this.applyInScopeAsync(function() {
            var pb = $scope.processblocker;
            pb.message = message;
            pb.block();
          });
        },
        unblock: function() {
          var $scope = this.$scope;
          if(!$scope)
            return;
          this.applyInScopeAsync(function() {
            $scope.processblocker.unblock();
          });
        },
        bindScope: function($scope) { this.$scope = $scope; },
      }
      gui.alerterrorbound = function() { gui.alerterror.apply(gui, arguments); }
      gui.unblockbound = function() { gui.unblock.apply(gui, arguments); }
      return gui;
    } ]);
