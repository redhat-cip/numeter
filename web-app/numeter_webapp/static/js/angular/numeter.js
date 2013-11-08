/*global window, angular, console*/
(function (window, angular) {
  'use strict';

  function parseGroups(hosts) {
    var group, host, title = '', groups = [];

    while (host = hosts.shift()) {

      if (host.group !== title) {
        group = {
          title: host.group || 'No group',
          hosts: []
        };
        groups.push(group);
        title = host.group;
      }
      group.hosts.push({
        id: host.id,
        name: host.name,
        categories: []
      });
    }
    return groups;
  }

  angular.module('numeter', ['ui.bootstrap']).
    directive('menu', ['$http', function ($http) {
      return {
        templateUrl: 'media/menu.html',
        link: function ($scope) {
          $http.get('api/host').
            success(function (data) {
              $scope.groups = parseGroups(data.objects);
            });
        },
        controller: ['$scope', '$http', function ($scope, $http) {
          $scope.loadCategories = function (hosts) {
            angular.forEach(hosts, function (host) {
              $http.get('hosttree/host/' + host.id).
                success(function (categories) {
                  host.categories = categories.map(function (category) {
                    return {name: category, plugins: []};
                  });
                });
            });
          };

          $scope.loadPlugins = function (categories, host_id) {
            angular.forEach(categories, function (category) {
              $http.get('hosttree/category/' + host_id, {params: {category: category.name}}).
                success(function (plugins) {                  
                  category.plugins = plugins;
                });
            });
          };
        }]
      };
    }]).
    controller('resolutionCtrl', ['$scope', function ($scope) {
      $scope.select = function (value) {
        $scope.$emit('resChange', value);
      };
    }]);
}(window, angular));
