angular.module('bucketlistApp')
  .controller('GUIGlobal', [ '$scope', '$element', '$q', 'gui',
    function guiGlobalController($scope, $element, $q, gui) {
      // main popup
      var mpopup = $scope.mainpopup = {
        title: '',
        body: '',
        hasclose: true,
        closelabel: 'Close',
        buttons: []
      };
      var mpopupResolvePopupPromise = null;
      
      mpopup.popup = function mainpopupPopup() {
        var $modal = $($element).find('.modal').first();
        $modal.modal('show');
        return $q(function(resolve) {
          mpopupResolvePopupPromise = function() {
            mpopupResolvePopupPromise = null;
            resolve();
          };
        });
      };
      mpopup.close = function mainpopupClose() {
        var $modal = $($element).find('.modal').first();
        if(!$modal.hasClass('in')) {
          var d = $q.defer();
          d.resolve();
          return d.promise;
        }
        return this.onClose();
      };
      mpopup.onClose = function mainpopupOnClose() {
        var $modal = $($element).find('.modal').first();
        $modal.modal('hide');
        return $q(function(resolve) {
          $modal.one('hidden.bs.modal', function() {
            if(mpopupResolvePopupPromise != null)
              mpopupResolvePopupPromise();
            resolve();
          })
        }); 
      };
      mpopup.onDismissed = function mainpopupOnDismissed(e) {
        var $modal = $($element).find('.modal').first(),
            modalEl = $modal[0];
        if(!modalEl)
          return;
        // bootstrap dismiss check
        if ( e.target.parentNode.getAttribute('data-dismiss') === 'modal' || e.target.getAttribute('data-dismiss') === 'modal' || e.target === modalEl ) {
          $modal.one('hidden.bs.modal', function() {
            if(mpopupResolvePopupPromise != null)
              mpopupResolvePopupPromise();
          })
        }
      };

      // progress blocker
      var pb = $scope.processblocker = {
        message: '',
        fadeIn: false,
        blocking: false,
        isBlocking: function() {
          return pb.blocking;
        },
        block: function() {
          pb.blocking = true;
          setTimeout(function() {
            $scope.$apply(function() {
              pb.fadeIn = true;
            });
          }, 10);
        },
        unblock: function() {
          pb.fadeIn = false;
          setTimeout(function() {
            $scope.$apply(function() {
              pb.blocking = false;
            });
          }, 500);
        }
      };

      // bind scope to gui service
      gui.bindScope($scope);
    } ]);
