/*global window, angular*/
(function (window, angular) {
  'use strict';

  angular.module('numeter', ['ui.bootstrap']);


  window.AccordionMenuCtrl = ['$scope', '$http', function ($scope, $http) {

    $http.get('api/host/').
      success(function (data) {
        var group, object, objects = data.objects, title = '';
        $scope.groups = [];

        while (object = objects.shift()) {

          if (object.group !== title) {            
            group = {
              title: object.group || 'No group',
              open: false,
              hosts: []
            };
            $scope.groups.push(group);
            title = object.group;
          }          
          group.hosts.push({
            id: object.id,
            url: object.resource_uri,
            name: object.name,
            categories: []
          });
        }
      }).
      error(function () {
        // numeter.error_modal();
      });

    $scope.loadHost = function (hosts) {
      angular.forEach(hosts, function (host) {
        $http.get('hosttree/host/' + host.id).
          success(function (data) {
            host.categories = data;
          }).
          error(function () {
            // numeter.error_modal();      
          });
      });
    };
  }];
}(window, angular));

    
    
