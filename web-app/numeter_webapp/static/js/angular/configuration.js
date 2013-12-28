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
                {title: "Plugin", content: "3", url: "/configuration/plugin", active:false},
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
        // TABS
        controller('InputFilterCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.q = 'root';
            $scope.updateInstances = function (q) {
                $scope.$emit('qChange', q);
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
        directive('mytab', function ($http) {
            return {
                restrict: 'A',
                replace: false,
                transclude: true,
                template: '<div ng-include="getTemplateUrl()"></div>',
                link: function ($scope) {
                    $http.get('/rest/users/', {params: {q: ''}}).
                        success(function (data) {
                            $scope.users = data.results;
                            $scope.next = data.next;
                            $scope.previous = data.previous;
                        });
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    console.log($scope.q);
                    $scope.$on('qChange', function (event, q) {
                        $http.get('/rest/users/', {params: {q: q}}).
                            success(function (data) {
                                $scope.users = data.results;
                                $scope.next = data.next;
                                $scope.previous = data.previous;
                            });
                        });
                }]
                    
            };
        }).
        controller('configurationTabCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.usertabs = [
                {title: "Users", content: "1", url: "/media/user_list.html", active: true},
                {title: "Superusers", content: "2", url: "/configuration/superuser/list", active:false},
                {title: "Groups", content: "3", url: "/configuration/group/list", active:false},
                {title: "Add user", content: "4", url: "/configuration/user/add", active:false},
                {title: "Add group", content: "4", url: "/configuration/group/add", active:false},
            ];
            $scope.tabs = $scope.usertabs;
            $scope.tabIndex = $scope.usertabs[0];

            $scope.showTab = function (tab) {
              $scope.tabIndex.active = false;
              $scope.tabIndex = tab;
              $scope.tabIndex.active = true;
            };

            $scope.getTemplateUrl = function () {
                return $scope.tabIndex.url;
            };

            $scope.openTab = function (title, url) {
                var new_tab = {title: title, url: url};
                $scope.usertabs.push(new_tab);
                $scope.tabIndex.active = false;
                $scope.tabIndex = new_tab;
                $scope.tabIndex.active = true;
            };
        }]);

}(angular));
