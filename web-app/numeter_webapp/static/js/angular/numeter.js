/*global window, angular, console*/
(function (angular) {
    'use strict';

    angular.module('numeter', ['ui.bootstrap', 'ngCookies'])
	.run( function run( $http, $cookies ){
	
	    // For CSRF token compatibility with Django
	    //$http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
	    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
	    $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
	})
        .directive('graph', ['$http', function ($http) {
            return {
                scope: {
                    resolution: '=',
                    url: '=',
                    graphname: '=',
                    hostid: '='
                },
                templateUrl: '/media/templates/graph.html',
                link: function ($scope, $element) {
                    numeter.get_graph($scope.url, $element[0], $scope.resolution);
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    console.log($scope.url);
                }]
            };
        }])
        .directive('menu', ['$http', function ($http) {
            return {
                templateUrl: '/media/templates/hosttree.html',
                scope: {
                    showGraphs: '&'
                },
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
                        // $scope.$emit('displayGraph', host.id, plugins);
                        $scope.showGraphs({id: host.id, plugins: plugins});
                    };

                    $scope.displayGraph = function (host_id, plugins, open) {
                        if (open) {
                            return;
                        }
                        // $scope.$emit('displayGraph', host_id, plugins);
                        $scope.showGraphs({id: host_id, plugins: plugins});
                    };

                }]
            };
        }])
        .controller('graphCtrl', ['$scope', '$http', '$location', function ($scope, $http, $location) {
            $scope.resolution = $location.search().resolution || 'Daily';
            $scope.graphs = [];

            $scope.showGraphs = function(hostID, plugins) {
                $scope.graphs.length = 0;
                angular.forEach(plugins, function (plugin) {
                    $scope.graphs.push({
                        url: "/rest/hosts/" + hostID + "/plugin_extended_data/?plugin=" + plugin.Plugin,
                        graphname: plugin.Plugin,
                        hostid: '' + hostID, //force string conversion
                        resolution: $scope.resolution
                    });
                });
            };

            $scope.changeRes = function (resolution) {
                $scope.resolution = resolution;
                //copy old graphs in order to render them again
                var old_graphs = angular.copy($scope.graphs);
                $scope.graphs.length = 0;
                angular.forEach(old_graphs, function (graph) {
                    $scope.graphs.push({
                        url: graph.url,
                        graphname: graph.graphname,
                        hostid: graph.hostid,
                        resolution: $scope.resolution
                    });
                })
            }
 
            var plugins     = $location.search().plugins;
            var host        = $location.search().host;
 
            if (plugins && host){
                $scope.showGraphs(host, [{Plugin: plugins}]);
            }
        }])
        .config(['$routeProvider', '$locationProvider', function AppConfig($routeProvider, $locationProvider) {
            // enable html5Mode for pushstate ('#'-less URLs)
            $locationProvider.html5Mode(true);
        }]);

}(angular));
