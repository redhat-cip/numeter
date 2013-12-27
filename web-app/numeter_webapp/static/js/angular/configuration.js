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
        directive('tab', function () {
            return {
                restrict: 'A',
                replace: false,
                transclude: true,
                template: '<div ng-include="getTemplateUrl()"></div>'
            };
        }).
        controller('configurationTabCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.usertabs = [
                {title: "Users", content: "1", url: "/configuration/user/list", active: true},
                {title: "Superusers", content: "2", url: "/configuration/superuser/list", active:false},
                {title: "Groups", content: "3", url: "/configuration/plugin", active:false},
                {title: "Add user", content: "4", url: "/configuration/view", active:false},
                {title: "Add group", content: "4", url: "/configuration/view", active:false},
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
        }]);

}(angular));
