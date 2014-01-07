/*global window, angular, console*/
(function (angular) {
    'use strict';
    angular.module('numeter', ['ui.bootstrap', 'ui.select2']).
        // MAINTABS
        directive('maintab', function () {
            return {
                restrict: 'A',
                replace: false,
                transclude: true,
                template: '<div ng-include="getTemplateUrl()"></div>'
            };
        }).
        controller('configurationMainTabCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.maintabs = [
                { title: "Users",
                  content: "1",
                  url: "/media/templates/configuration/maintab.html",
                  active: true,
                  rest_urls: [
                    ['/rest/users/', 'users'],
                    ['/rest/superusers/', 'superusers'],
                    ['/rest/groups/', 'groups']
                  ]
                },
                { title: "Storage",
                  content: "2",
                  url: "/media/templates/configuration/maintab.html",
                  active:false,
                  rest_urls: [
                    ['/rest/storages/', 'storages'],
                    ['/rest/hosts/', 'hosts'],
                  ]
                },
                { title: "Plugin",
                  content: "3",
                  url: "/media/templates/configuration/maintab.html",
                  active:false,
                  rest_urls: [
                    ['/rest/plugins/', 'plugins'],
                    ['/rest/sources/', 'sources'],
                  ]
                },
                { title: "View",
                  content: "4",
                  url: "/media/templates/configuration/maintab.html",
                  active: false,
                  rest_urls: [
                    ['/rest/views/', 'views'],
                    ['/rest/multiviews/', 'multiviews'],
                    ['/rest/skeletons/', 'skeletons'],
                  ]
                },
            ];
            $scope.maintabIndex = $scope.maintabs[0];

            $scope.showMainTab = function (maintab) {
              $scope.maintabIndex.active = false;
              $scope.maintabIndex = maintab;
              $scope.maintabIndex.active = true;
            };
            $scope.getTemplateUrl = function () {
                return $scope.maintabIndex.url;
            };
        }]).
        controller('InputFilterCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.q = '';
            $scope.updateInstances = function (q) {
                $scope[$scope.tab.model].q = q;
                $scope.$emit('qChange', $scope.tab.model);
            };
        }]).
        directive('ngEnter', function () {
            return function (scope, element, attrs) {
                element.bind("keydown keypress", function (event) {
                    if(event.which === 13) {
                        scope.$apply(function (){
                            scope.$eval(attrs.ngEnter);
                        });
                        event.preventDefault();
                    }
                });
            };
        }).
        // TABS
        directive('mytab', function ($http) {
            return {
                restrict: 'A',
                replace: false,
                transclude: true,
                template: '<div ng-include="getTemplateUrl()"></div>',
                link: function ($scope) {
                    $.each($scope.maintab.rest_urls, function(i, rest_url) {
                      $http.get(rest_url[0]).success(function (data) { $scope[rest_url[1]] = data; });
                    });
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    $scope.$on('qChange', function (event, model) {
                        var q = $scope[model].q;
                        $http.get($scope.tab.rest_url, {params: {q: q}}).
                            success(function (data) {
                                $scope[model] = data;
                                $scope[model].q = q;
                            });
                        });
                    // SWITCH BETWEEN PAGES
                    $scope.$on('pageChange', function (event, url, model) {
                        $http.get(url).
                            success(function (data) {
                                var q = $scope[model].q;
                                $scope[model] = data;
                                $scope[model].q = q;
                            });
                        });
                    $scope.changePage = function (url, model) {
                        if (url) $scope.$emit('pageChange', url, model);
                    };
                }]
                    
            };
        }).
        controller('configurationTabCtrl', ['$scope', '$http', function ($scope, $http) {
            // DEFINE USER TABS
            $scope.usertabs = [
                { title: "Users",
                  content: "1",
                  url: "/media/templates/configuration/user_list.html",
                  active: true,
                  static: true,
                  rest_url:'/rest/users/',
                  model: 'users',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/users/', method:'DELETE', model:'user'}
                  ]
                },
                { title: "Superusers",
                  content: "2",
                  url: "/media/templates/configuration/superuser_list.html",
                  static: true,
                  active: false,
                  rest_url: '/rest/superusers/',
                  model: 'superusers',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/users/', method:'DELETE', model:'superuser'}
                  ]
                },
                { title: "Groups",
                  content: "3",
                  url: "/media/templates/configuration/group_list.html",
                  static: true,
                  active: false,
                  rest_url:'/rest/groups/',
                  model: 'groups',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/groups/', method:'DELETE', model:'group'}
                  ]
                },
                { title: "Add user",
                  content: "4",
                  url: "/configuration/user/add",
                  static: true,
                  active: false,
                  rest_url: '/rest/users/',
                  model: 'user',
                  multiple_fields: {'groups': [] }
                },
                { title: "Add group",
                  content: "5",
                  url: "/configuration/group/add",
                  static: true,
                  active: false,
                  rest_url: '/rest/groups/',
                  model: 'group'
                },
            ];
            $scope.maintabs[0].tabs = $scope.usertabs;
            // STORAGE TABS
            $scope.storagetabs = [
                { title: "Storages",
                  content: "1",
                  url: "/media/templates/configuration/storage_list.html",
                  active: true,
                  static: true,
                  rest_url:'/rest/storages/',
                  model: 'storages',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/storages/', method:'DELETE', model:'storage'}
                  ]
                },
                { title: "Hosts",
                  content: "2",
                  url: "/media/templates/configuration/host_list.html",
                  active: false,
                  static: true,
                  rest_url:'/rest/hosts/',
                  model: 'hosts',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/hosts/', method:'DELETE', model:'host'}
                  ]
                },
                { title: "Add storage",
                  content: "3",
                  url: "/configuration/storage/add",
                  active: false,
                  static: true,
                  rest_url:'/rest/storages/',
                  model: 'storage',
                },
            ];
            $scope.maintabs[1].tabs = $scope.storagetabs;
            // Plugins TABS
            $scope.plugintabs = [
                { title: "Plugins",
                  content: "1",
                  url: "/media/templates/configuration/plugin_list.html",
                  active: true,
                  static: true,
                  rest_url:'/rest/plugins/',
                  model: 'plugins',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/plugins/', method:'DELETE', model:'plugin'}
                  ]
                },
                { title: "Sources",
                  content: "2",
                  url: "/media/templates/configuration/source_list.html",
                  active: false,
                  static: true,
                  rest_url:'/rest/sources/',
                  model: 'plugins',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/sources/', method:'DELETE', model:'source'}
                  ]
                },
            ];
            $scope.maintabs[2].tabs = $scope.plugintabs;
            // VIEW TABS
            $scope.viewtabs = [
                { title: "Views",
                  content: "1",
                  url: "/media/templates/configuration/view_list.html",
                  active: true,
                  static: true,
                  rest_url:'/rest/views/',
                  model: 'views',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/views/', method:'DELETE', model:'view'}
                  ]
                },
                { title: "Multiviews",
                  content: "2",
                  url: "/media/templates/configuration/multiview_list.html",
                  active: false,
                  static: true,
                  rest_url:'/rest/multiviews/',
                  model: 'multivews',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/multiviews/', method:'DELETE', model:'multiview'}
                  ]
                },
                { title: "Skeletons",
                  content: "3",
                  url: "/media/templates/configuration/skeleton_list.html",
                  active: false,
                  static: true,
                  rest_url:'/rest/skeletons/',
                  model: 'multivews',
                  list_actions: [
                    {name:'Delete', value:'', url:'/rest/skeletons/', method:'DELETE', model:'skeleton'}
                  ]
                },
                { title: "Add view",
                  content: "4",
                  url: "/configuration/view/add",
                  active: false,
                  static: true,
                  rest_url:'/rest/views/',
                  model: 'view',
                  multiple_fields: {'sources': [] }
                },
                { title: "Add multiview",
                  content: "5",
                  url: "/configuration/multiview/add",
                  active: false,
                  static: true,
                  rest_url:'/rest/multiviews/',
                  model: 'multiview',
                  multiple_fields: {'views': [] }
                },
                { title: "Add skeleton",
                  content: "6",
                  url: "/configuration/skeleton/add",
                  active: false,
                  static: true,
                  rest_url:'/rest/skeletons/',
                  model: 'skeleton',
                },
            ];
            $scope.maintabs[3].tabs = $scope.viewtabs;
            // DEFINE TAB
            $scope.tabs = $scope.maintab.tabs;
            $scope.tabIndex = $scope.maintab.tabs[0];

            $scope.showTab = function (tab) {
              $scope.tabIndex.active = false;
              $scope.tabIndex = tab;
              // if (tab.static === true) $scope.$emit('qChange', tab.model);
              $scope.tabIndex.active = true;
            };

            $scope.getTemplateUrl = function () {
                // RETURN APPROPIRATE TO STATIC OR DYNAMIC TAB
                if ($scope.tabIndex.instance) {
                    $scope.tabIndex.form = $scope.tabIndex.instance;
                    return $scope.tabIndex.templateUrl;
                }
                return $scope.tabIndex.url;
            };

            // CREATE A CLOSABLE DYNAMIC TAB FOR INSTANCES
            $scope.createTab = function (instance, type) {
                var new_tab;
                // SERACH IF TAB IS ALREADY CREATED
                for (var i = 0, len = $scope.tabs.length; i < len; ++i) {
                    if ($scope.tabs[i].instance == instance) {
                        new_tab = $scope.tabs[i];
                        break;
                    }
                }
                if (!new_tab) {
                  var multiple_fields = {};
                  angular.forEach(instance, function(v, k){
                    if( Object.prototype.toString.call(v) === '[object Array]' ) {
                      this[k] = v;
                    } 
                  }, multiple_fields);
                  new_tab = {
                      title: instance.name || instance.username,
                      url: instance.url,
                      instance: instance,
                      multiple_fields: multiple_fields,
                      templateUrl: '/configuration/' + type + '/' + instance.id
                  };
                  $scope.tabs.push(new_tab);
                }
                $scope.tabIndex.active = false;
                $scope.tabIndex = new_tab;
                $scope.tabIndex.active = true;
            };
            // CLOSE TABS
            $scope.closeTab = function (tab) {
                var index = $scope.tabs.indexOf(tab);
                $scope.showTab($scope.tabs[0]);
                $scope.tabs.splice(index, 1);
            };
        }]).
        controller('MyFormCtrl', ['$scope', '$http', function ($scope, $http) {
            // Set form metal-data
            if (! $scope.tabIndex.instance) {
                $scope.method = 'POST';
                $scope.url = $scope.tabIndex.rest_url;
            } else {
                $scope.method = 'PATCH';
                $scope.url = $scope.tabIndex.form.url;
            }
            // Form submit
            $scope.submit = function() {
                $http({
                    method: $scope.method,
                    url: $scope.url,
                    data: $scope.tabIndex.form,
                    dataType: 'json',
                    responseType: 'json',
                    headers: {"Content-Type": "application/json"}
                }).
                    success(function (data) {
                        // Create tab for new
                        if ($scope.method == 'POST') $scope.createTab(data, $scope.tab.model);
                    });
            };
            // DELETE BTN
            $scope.delete_instance = function() {
                $http({
                    method: 'DELETE',
                    url: $scope.url
                }).
                    success(function (data) {
                        $scope.closeTab($scope.tab);
                    });
            };
            // SELECT2
            var $setPristine = function(input){ return 1;};
            $scope.remote_select = $scope.remote_select || {};
            angular.forEach($scope.tabIndex.multiple_fields, function(v, model){
              $scope.remote_select[model] = {
                  ajax: {
                      url: '/rest/' + model + '/',
                      dataType: 'json',
                      data: function (term, page) { return { q: term }; },
                      results: function (data, page) { return {results: data.results}; },
                      headers: {"Content-Type": "application/json"}
                  },
                  initSelection: function(element, callback) {
                          // IF ALREADY INIT OR NOT
                          if ( Object.prototype.toString.call($scope.tabIndex.form[model][0]) !== '[object Number]') { 
                              callback($scope.tabIndex.form[model]); 
                          } else {
                            $http({
                                method: 'GET',
                                url: '/rest/' + model + '/',
                                params: {'id': $scope.tabIndex.form[model] },
                                responseType: 'json',
                            }).success(function(data) {
                                callback(data.results);
                            });
                          }
                  },
              };
            });
        }]).
        controller('ListActionCtrl', ['$scope', '$http', function ($scope, $http) {
            // SET OPTIONS
            $scope.list_actions = $scope.tabIndex.list_actions;
            $scope.selected_list_action = $scope.list_actions[0];
            // LAUNCH ACTION
            $scope.launch_action = function() {
                var ids = [];
                $('.'+ $scope.selected_list_action.model +'-checkbox:checked').each( function() {
                    ids.push( $(this).attr('name') );
                });
                $http({
                    method: $scope.selected_list_action.method,
                    url: $scope.selected_list_action.url,
                    data: {'id': ids},
                    headers: {"Content-Type": "application/json"}
                }).
                    success(function (data) {
                        // MAKE POST ACTION
                        var model = $scope.selected_list_action.model;
                        if ($scope.selected_list_action.method == 'DELETE') {
                            $.each($scope[model+'s'].results, function(i,v) {
                                if ( $.inArray(String(v.id), ids) === 0 ) {
                                    $scope.$emit('qChange', model+'s');
                                }
                            });
                        }
                    });
            };
        }]);

}(angular));
