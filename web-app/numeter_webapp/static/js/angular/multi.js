/*global window, angular, console*/
(function (angular) {
    'use strict';

    angular.module('numeter', ['ui.bootstrap']).
        directive('multiviews', ['$http', function ($http) {
            return {
                templateUrl: '/media/templates/multiview.html',
                link: function ($scope, $element) {
                    $http.get('/rest/multiviews/').
                        success(function (data) { $scope.multiviews = data.results; });
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    $http.get('/rest/multiviews/').
                        success(function (data) { $scope.multiviews = data.results; });

                    $scope.displayViews = function (multiview) {
                        angular.forEach(multiview.views, function (view_id) {
                          $scope.$emit('displayView', view_id);
                        });
                    };
                }]
            };
        }]).
        controller('resolutionCtrl', ['$scope', function ($scope) {
            $scope.select = function (value) {
                $scope.$emit('resChange', value);
            };
        }]).
        controller('viewCtrl', ['$scope', function ($scope) {
            $scope.selected = 'Daily';
            $scope.$on('resChange', function (event, resolution) {
                $scope.selected = resolution;
            });

             $scope.$on('resChange', function (event) {
                var old_graphs = $scope.graphs;
                $scope.graphs = [];
                old_graphs.map(function (graph) {
                    this.push({url: graph.url, resolution: $scope.selected });
                }, $scope.graphs);
             });
        }]).
        directive('view', ['$http', function ($http) {
            return {
                scope: {
                    resolution: '=',
                    url: '=',
                    id: '=',
                },
                templateUrl: '/media/templates/graph.html',
                link: function ($scope, $element) {
                    if ($scope.id) {
                        var res = 'Daily';
                        var url = '/rest/views/' + $scope.id + '/extended_data/';
                        numeter.get_graph(url, $element[0], res);
                    }
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    // DISPLAY VIEWS
                    $scope.$on('displayView', function (event, view_id) {
                        debugger;
                    });
                }]
            };
        }]);

}(angular));
