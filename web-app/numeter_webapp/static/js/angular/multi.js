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
                    // SET RES
                    $scope.resolution = 'Daily';

                    $scope.displayViews = function (multiview) {
                        angular.forEach(multiview.views, function (view_id) {
                          $scope.$emit('displayView', view_id);
                        });
                    };
                    // FILTER MVIEWS
                    $scope.$on('qChange', function (event, q) {
                        $http.get('/rest/multiviews/', {params: {q: q}}).
                            success(function (data) {
                                $scope.multiviews = data.results;
                            });
                        });
                    // UPDATE RES OF OPENED MVIEW
                    $scope.$on('resChange', function (event) {
                        angular.forEach($scope.multiviews, function (multiview) {
                            if (!multiview.opened) $scope.displayViews(multiview);
                        });
                    });
                }]
            };
        }]).
        // SEARCH INPUT
        controller('InputFilterCtrl', ['$scope', '$http', function ($scope, $http) {
            $scope.q = '';
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
        // RESOLUTION INPUTS
        controller('resolutionCtrl', ['$scope', function ($scope) {
            $scope.resolution = 'Daily';
            $scope.select = function (value) {
                $scope.$emit('resChange', value);
            };
        }]).
        controller('viewCtrl', ['$scope', function ($scope) {
            $scope.$on('resChange', function (event, resolution) {
                $scope.resolution = resolution;
            });
        }]).
        directive('view', ['$http', function ($http) {
            return {
                scope: {
                    resolution: '=',
                    url: '=',
                    multiview: '=',
                    id: '=',
                },
                templateUrl: '/media/templates/graph.html',
                link: function ($scope, $element) {
                    if ($scope.id) {
                        var res = $scope.resolution;
                        var url = '/rest/views/' + $scope.id + '/extended_data/?';
                        numeter.get_graph(url, $element[0], res);
                    }
                },
                controller: ['$scope', '$http', function ($scope, $http) {
                    $scope.$on('displayView', function (event) {
                        angular.forEach($scope.multiviews, function (multiview) {
                            if (multiview.opened) $scope.displayViews(multiview);
                        });
                    });
                    console.log($scope.url);
                }]
            };
        }]);

}(angular));
