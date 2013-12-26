/*global window, angular, console*/
(function (angular) {
    'use strict';
    angular.module('numeter', ['ui.bootstrap']).
        directive('configuration', function () {
            return {
                restrict: 'A',
                replace: false,
                transclude: true,
                template: '<div ng-include="getTemplateUrl()"></div>'

            };
        }).

        controller('configurationMainTabCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.maintabs = [
                {title: "Users", content: "", url: "/configuration/user"},
                {title: "Storage", content: "", url: "/configuration/storage"},
                {title: "Plugin", content: "", url: "/configuration/plugin"},
                {title: "View", content: "", url: "/configuration/view"},
            ];
            $scope.tabs = [
                {title: "View", content: "", url: "/configuration/view" },
            ];
            $scope.maintab = $scope.maintabs[0];

            $scope.showMainTab = function (maintab) {
            $scope.maintab = maintab;
              // $http.get(maintab.url).
              //   success(function (data) {
              //       console.log(data);
              //     maintab.content = data;
              //   });
            };
            $scope.getTemplateUrl = function () {
                return $scope.maintab.url;
            };
        }]);

}(angular));
