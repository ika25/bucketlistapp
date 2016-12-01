angular.module('bucketlistApp')
  .component('todoManage', {
    templateUrl: 'todo-manage.template.html',
    controller: [ '$scope', 'gui', 'userService', '$route', '$location', 
      function($scope, gui, userService, $route, $location) {
        function parseItemsScroll(v) {
          var split = v.split('-');
          if(split.length != 2 || isNaN(parseInt(split[0])) ||
             isNaN(parseInt(split[1]))) {
            return { offset: 0, limit: 10 };
          }
          return { offset: parseInt(split[0]),
                   limit: Math.max(1, parseInt(split[1])) };
        }
        function mkItemsScroll(offset, limit) {
          return Math.max(0, parseInt(offset)) + '-' + Math.max(1, parseInt(limit));
        }
        function selectOptionIndexOf(value, items) {
          for(var i = 0, len = items.length; i < len; ++i) {
            if(items[i].value == value)
              return i;
          }
          return -1;
        }
        function mkLimitOpt(limit) {
          return { value: ''+limit, label: limit + ' Items per page' };
        }
        function transformTodoItem(item) {
          item.checked = item.checked ? true : false;
          return item;
        }
        function pagesListUpdate() {
          var count = self.count,
              offset = self.offset, limit = self.limit;
          if(!(count > 0 && offset >= 0 && limit > 0)) {
            self.pagesList = [];
            self.hasMoreLeft = false;
            self.hasMoreRight = false;
            return;
          }
          var pmamount = self.pagingMaxAmount,
              pageCount = Math.ceil(count / limit),
              page = Math.floor(offset / limit) + 1,
              plen_half = Math.min(pageCount - page + 1, pmamount / 2.0),
              startpage = Math.max(1, page - Math.floor(pmamount - plen_half)),
              splen = Math.min(pageCount - startpage + 1, pmamount);
          var ret = [];
          for(var i = 0; i < splen; ++i) {
            ret.push((startpage + i)+'');
          }
          self.pagesList = ret;
          self.hasMoreLeft = startpage > 1;
          self.hasMoreRight = startpage + splen - 1 < pageCount;
        }
        var self = this;
        var itemsScroll = $route.current.params['itemsScroll'] || '',
            itemsScrollV = parseItemsScroll(itemsScroll);
        $.extend(self, {
          pagingMaxAmount: 10,
          limits: [ mkLimitOpt(10), mkLimitOpt(20), mkLimitOpt(50), mkLimitOpt(100) ],
          loading: false,
          fields: [
            {
              type: 'CHECKBOX',
              label: 'Checked',
              title: 'Done',
              fit: true,
              key: 'checked',
              onChange: function(item) {
                self.loading = true;
                userService.todo.update({ id: item.id }, {
                  checked: item.checked ? 1 : 0
                }).$promise.then(function(record) {
                  var idx = self.items.indexOf(item);
                  if(idx != -1) {
                    self.items[idx] = transformTodoItem(record);
                  }
                }).finally(function() { self.loading = false })
                  .catch(gui.alerterrorbound);
              }
            },
            {
              type: 'IMAGE',
              label: '',
              key: 'image',
              fit: true,
              textcenter: true
            },
            {
              type: 'TEXT',
              label: 'Title',
              key: 'title',
            },
            {
              type: 'BUTTON',
              label: '',
              title: 'Edit',
              hidetitle: true,
              btntype: 'primary',
              fa_icon: 'pencil',
              fit: true,
              onClick: function(item) {
                $location.path('/todo/edit/' + item.id);
              }
            },
            {
              type: 'BUTTON',
              label: '',
              title: 'Delete',
              hidetitle: true,
              btntype: 'danger',
              fa_icon: 'trash',
              fit: true,
              onClick: function(item) {
                gui.confirm('Request to delete item "'+item.title+'"',
                            "Are you sure you want to delete it?", 'danger')
                  .then(function(confirmed) {
                    gui.blockloading();
                    userService.todo.delete({ id: item.id }).$promise
                      .then(function() { loadItems(); })
                      .finally(gui.unblockbound)
                      .catch(gui.alerterrorbound);
                  });
              },
            }
          ],
          pageRoutePrefix: '/todo/manage/',
          selectOptionIndexOf: selectOptionIndexOf,
          mkItemsScroll: function(offset) {
            console.log(mkItemsScroll(offset, self.limit));
            return mkItemsScroll(offset, self.limit);
          },

          onLimitChange: function() {
            self.limit = parseInt(self._limit.value);
            var path = self.pageRoutePrefix + mkItemsScroll(self.offset, self.limit);
            $location.path(path);
          },
          
          itemsScroll: itemsScroll,
          offset: itemsScrollV.offset,
          limit: itemsScrollV.limit,
          _limit: mkLimitOpt(itemsScrollV.limit),
          items: [],
          count: 0,
          pagesList: [],
          hasMoreLeft: false,
          hasMoreRight: false
        });
        if(selectOptionIndexOf(self.limit, self.limits) == -1)
          self.limits.unshift(mkLimitOpt(self.limit));
        loadItems();
        function loadItems() {
          self.loading = true;
          userService.todo.list({
            offset: self.offset,
            limit: self.limit,
            order_by: 'created_at desc'
          }).$promise.then(function(data) {
            self.loading = false;
            var items = [];
            for(var i = 0, len = data.records.length; i < len; ++i)
              items.push(transformTodoItem(data.records[i]));
            self.items = items;
            self.count = data.count;
            pagesListUpdate()
          }).catch(gui.alerterrorbound);
        }
        
      } ]
  });
