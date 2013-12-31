/*global window, angular, console*/
(function (angular) {
    'use strict';
    angular.module('numeter', ['ui.bootstrap']).
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
                {title: "Users", content: "1", url: "/media/conf_user.html", active: true},
                {title: "Storage", content: "2", url: "/configuration/storage", active:false},
                {title: "Plugin", content: "3", url: "/configuration/elugin", active:false},
                {title: "View", content: "4", url: "/configuration/view", active:false},
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
                $scope.$emit('qChange', q, $scope.tab.model);
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
                    $http.get('/rest/users/').success(function (data) { $scope.users = data; });
                    $http.get('/rest/groups/').success(function (data) { $scope.groups = data; });
                    $http.get('/rest/superusers/').success(function (data) { $scope.superusers = data; });
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    console.log($scope);
                    $scope.$on('qChange', function (event, q, model) {
                        $http.get($scope.tab.list_url, {params: {q: q}}).
                            success(function (data) {
                                $scope[model] = data;
                            });
                        });
                }]
                    
            };
        }).
        controller('configurationTabCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.usertabs = [
                {title: "Users", content: "1", url: "/media/user_list.html", active: true, static: true, list_url:'/rest/users/', model: 'users'},
                {title: "Superusers", content: "2", url: "/media/superuser_list.html", static: true, active:false, list_url: '/rest/superusers'},
                {title: "Groups", content: "3", url: "/media/group_list.html", static: true, active:false, list_url:'/rest/groups/', model: 'groups'},
                {title: "Add user", content: "4", url: "/configuration/user/add", static: true, active: false, data_url: '/rest/users/', model: 'user'},
                {title: "Add group", content: "5", url: "/configuration/group/add", static: true, active: false, data_url: '/rest/groups/', model: 'group'},
            ];
            $scope.tabs = $scope.usertabs;
            $scope.tabIndex = $scope.usertabs[0];

            $scope.showTab = function (tab) {
              $scope.tabIndex.active = false;
              $scope.tabIndex = tab;
              $scope.tabIndex.active = true;
            };

            $scope.getTemplateUrl = function () {
                if ($scope.tabIndex.instance) {
                    $scope.form = $scope.tabIndex.instance;
                    return $scope.tabIndex.templateUrl;
                }
                return $scope.tabIndex.url;
            };

            // CREATE A CLOSABLE DYNAMIC TAB FOR INSTANCES
            $scope.createTab = function (instance, type) {
                var new_tab;
                // SERACH IF TAB IS ALREADY CREATED
                for (var i = 0, len = $scope.usertabs.length; i < len; ++i) {
                    if ($scope.usertabs[i].instance == instance) {
                        new_tab = $scope.usertabs[i];
                        break;
                    }
                }
                if(!new_tab) {
                  new_tab = {
                      title: instance.name || instance.username,
                      url: instance.url,
                      instance: instance,
                      templateUrl: '/configuration/' + type + '/' + instance.id
                  };
                  $scope.usertabs.push(new_tab);
                }
                $scope.tabIndex.active = false;
                $scope.tabIndex = new_tab;
                $scope.tabIndex.active = true;
            };
            // CLOSE TABS
            $scope.closeTab = function (tab) {
                var index = $scope.tabs.indexOf(tab);
                if(tab.active) {
                    $scope.tabIndex = $scope.tabs[0];
                    $scope.tabIndex.active = true;
                }
                $scope.tabs.splice(index, 1);
            };
        }]).
        controller('MyFormCtrl', ['$scope', '$http', function ($scope, $http) {
            // Set form metal-data
            if (! $scope.tabIndex.instance) {
                $scope.method = 'POST';
                $scope.url = $scope.tabIndex.data_url;
            } else {
                $scope.method = 'PATCH';
                $scope.url = $scope.form.url;
            }
            // Form submit
            $scope.submit = function() {
                $http({
                    method: $scope.method,
                    url: $scope.url,
                    data: $scope.form,
                    headers: {"Content-Type": "application/json"}
                }).
                    success(function (data) {
                        // Create tab for new
                        if ($scope.method == 'POST') $scope.createTab(data, $scope.tab.model);
                    });
            };
        }]);


}(angular));
