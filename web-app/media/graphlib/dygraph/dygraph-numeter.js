/*global Dygraph, window, document, jQuery*/
(function (window, document, $) {
  'use strict';
  //// SET GRAPH
  var numeter;
  numeter = window.numeter = window.numeter || {};
  numeter.preview_request = null;

  // GET SIMPLE GRAPH
  numeter.get_simple_graph = function (url, into_id) {
    numeter.preview_request = $.getJSON(url, function (data) {
      var g, i, length = data.datas.length;
      for (i = 0; i < length; i = i + 1) {
        data.datas[i][0] = new Date(data.datas[i][0] * 1000);
      }
      g = new Dygraph(
        document.getElementById(into_id),
        data.datas,
        { labels: data.labels,
          colors: data.colors,
          pixelsPerLabel: 60,
          gridLineWidth: 0.1,
          labelsKMG2: true,
          height: 150 }
      );
      numeter.graphs.push(g);
    });
  };
  // GET ADVANCED GRAPH
  numeter.get_graph = function (url, into, res) {
    $.getJSON(url + '?res=' + res, function (data) {
      // Compute width
      var i, g,
        length = data.datas.length,
        width = $('.collapse').css('width').replace('px', '') / 2 - 50;
      // Make date
      for (i = 0; i < length; i = i + 1) {
        data.datas[i][0] = new Date(data.datas[i][0] * 1000);
      }

      g = new Dygraph(
        document.getElementById(into),
        data.datas,
        {
          title: data.name,
          height: 250,
          width: width,
          legend: 'always',
          fillGraph: true,
          pixelsPerLabel: 60,
          gridLineWidth: 0.1,
          strokeWidth: 1.5,
          colors: data.colors,
          showRangeSelector: true,
          highlightCircleSize: 4.0,
          labels: data.labels,
          labelsKMG2: true,
          labelsSeparateLines: true,
          labelsDivWidth: 300,
          labelsDivStyles: {
            backgroundColor: 'rgba(200, 200, 200, 0.20)',
            borderRadius: '10px',
            padding: '4px'
          },
          axes: {
            y: {
              axisLabelWidth: 30000
            }
          },
          series: {
            warning: {
              fillGraph: false,
              strokeWidth: 1.0,
              highlightCircleSize: 0.0
            },
            critical: {
              fillGraph: false,
              strokeWidth: 1.0,
              highlightCircleSize: 0.0
            }
          }
        }
      );
      g.url = url;
      numeter.graphs.push(g);
    });
  };

  // UPDATE GRAPH
  numeter.update_graph = function (graph, res) {
    $.getJSON(graph.url + '?res=' + res, function (data) {
      var i, length = data.datas.length;
      for (i = 0; i < length; i = i + 1) {
        data.datas[i][0] = new Date(data.datas[i][0] * 1000);
      }
      graph.updateOptions({
        file: data.datas,
        labels: data.labels,
        colors: data.colors
      });
    });
  };

}(window, document, jQuery));