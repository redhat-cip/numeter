/*global window, angular, console*/
(function (angular) {
  'use strict';
  angular.module('numeter', ['ui.bootstrap']).
    controller('configurationMainTabCtrl', ['$scope', '$http', function ($scope, $http) {
      $scope.maintabs = [
        { title:"Users", content:"", url:"/configuration/user" },
        { title:"Storage", content:"", url:"/configuration/storage" },
        { title:"Plugin", content:"", url:"/configuration/plugin" },
        { title:"View", content:"", url:"/configuration/view" },
      ];

      $scope.showMainTab = function (maintab) {
        $.ajax({
          url: maintab.url,
          success: function(data){
             console.log(data);
             maintab.content = data;
          }
        });
        // $http.get(maintab.url).
        //   success(function (data) {
        //       console.log(data);
        //     maintab.content = data;
        //   });
      };
    }]);

}(angular));
