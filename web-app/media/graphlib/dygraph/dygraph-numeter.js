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
      // Convert time to Date obj
      var g, i, length = data.datas.length;
      for (i = 0; i < length; i = i + 1) {
        data.datas[i][0] = new Date(data.datas[i][0] * 1000);
      }
      // Make series
      var source_name = data.labels[1];
      var series = {};
      // Stacked or not
      var is_stacked = false;
      for ( var i in data.infos ) {
        if ( data.infos[i].draw !== undefined ) {
          if ( data.infos[i].draw.indexOf('STACK') != -1 ) is_stacked = true;
        }
      }
      // Make series
      var series = {}
      for ( var source in data.infos ) {
        series[source] = {}
        if ( data.infos[source].draw !== undefined ) {
          if ( data.infos[source].draw.indexOf("AREA") != -1 ) { 
              series[source]['fillGraph'] = true;
          }
        }
      }

      g = new Dygraph(
        document.getElementById(into_id),
        data.datas,
        { labels: data.labels,
          colors: data.colors,
          pixelsPerLabel: 60,
          gridLineWidth: 0.1,
          labelsKMG2: true,
          series: series,
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
      // Stacked or not
      var is_stacked = false;
      for ( var i in data.infos ) {
        if ( data.infos[i].draw !== undefined ) {
          if ( data.infos[i].draw.indexOf('STACK') != -1 ) is_stacked = true;
        }
      }
      // Make series
      var series = {}
      for ( var source in data.infos ) {
        series[source] = {}
        if ( data.infos[source].draw !== undefined ) {
          if ( data.infos[source].draw.indexOf("AREA") != -1 ) { 
              series[source]['fillGraph'] = true;
          }
        }
      }
      series.warning = {
        fillGraph: false,
        strokeWidth: 1.0,
        highlightCircleSize: 0.0
      }
      series.critical = {
        fillGraph: false,
        strokeWidth: 1.0,
        highlightCircleSize: 0.0
      }

      g = new Dygraph(
        document.getElementById(into),
        data.datas,
        {
          title: data.name,
          series: series,
          height: 220,
          //width: width,
          legend: 'always',
          //fillGraph: true,
          pixelsPerLabel: 60,
          gridLineWidth: 0.1,
          strokeWidth: 1.5,
          colors: data.colors,
          showRangeSelector: true,
          highlightCircleSize: 4.0,
          stackedGraph: is_stacked,
          labels: data.labels,
          labelsDiv: document.getElementById('graph-labels-' + data.name),
          labelsKMG2: true,
          labelsSeparateLines: true,
          //labelsDivWidth: 300,
          labelsDivStyles: {
            backgroundColor: 'rgba(200, 200, 200, 0.20)',
            borderRadius: '10px',
            padding: '4px'
          },
          //axes: {
          //  y: {
          //    axisLabelWidth: 30000
          //  }
          //}
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
      // MAKE DATES
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
