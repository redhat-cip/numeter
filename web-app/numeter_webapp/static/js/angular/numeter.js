/*global window, angular, console*/
(function (angular) {
    'use strict';

    angular.module('numeter', ['ui.bootstrap']).
        directive('graph', ['$http', function ($http) {
            return {
                scope: {
                    resolution: '=',
                    url: '=',
                },
                templateUrl: 'media/templates/graph.html',
                link: function ($scope, $element) {
                    numeter.get_graph($scope.url, $element[0], $scope.resolution);
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    console.log($scope.url);
                }]
            };
        }]).
        directive('menu', ['$http', function ($http) {
            return {
                templateUrl: '/media/templates/hosttree.html',
                link: function ($scope) {
                    $http.get('rest/hosts/').
                        success(function (data) {
                            $scope.hosts = data.results;
                        });
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    // LOAD HOST'S PLUGINS AND SORT BY CATEGORY
                    $scope.loadCategories = function (host) {
                            $http.get('/wide-storage/list?host=' + host.hostid).
                                success(function (data) {
                                    host.categories = {};
                                    angular.forEach(data, function (plugin) {
                                        var category = plugin.Category;
                                        if (! host.categories[category]) host.categories[category] = {plugins: [], open: false, name: category};
                                        host.categories[category].plugins.push(plugin);
                                    });
                                });
                    };

                    $scope.loadPlugins = function (host, chosen_category) {
                        var plugins = angular.forEach(host.categories[chosen_category.name].plugins, function () {});
                        $scope.$emit('displayGraph', host.id, plugins);
                    };

                    $scope.displayGraph = function (host_id, plugins, open) {
                        if (open) {
                            return;
                        }
                        $scope.$emit('displayGraph', host_id, plugins);
                    };

                }]
            };
        }]).
        controller('resolutionCtrl', ['$scope', function ($scope) {
            $scope.select = function (value) {
                $scope.$emit('resChange', value);
            };
        }]).
        controller('graphCtrl', ['$scope', function ($scope) {
            $scope.selected = 'Daily';
            $scope.$on('resChange', function (event, resolution) {
                $scope.selected = resolution;
            });

            $scope.$on('displayGraph', function (event, host_id, plugins) {
                $scope.graphs = [];
                plugins.map(function (plugin) {          
                  this.push({url: "/get/graph/" + host_id + "/" + plugin.Plugin, resolution: $scope.selected });
                }, $scope.graphs);
             });
             $scope.$on('resChange', function (event) {
                var old_graphs = $scope.graphs;
                $scope.graphs = [];
                old_graphs.map(function (graph) {
                    this.push({url: graph.url, resolution: $scope.selected });
                }, $scope.graphs);
             });
      }]);

}(angular));
