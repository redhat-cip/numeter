/*global Dygraph, window, document, jQuery*/
(function (window, document, $) {
  'use strict';
  //// SET GRAPH
  var numeter;
  numeter = window.numeter = window.numeter || {};
  numeter.preview_request = null;

  // GET SIMPLE GRAPH
  numeter.get_simple_graph = function (url, into) {
    numeter.preview_request = $.getJSON(url, function (data) {

      var start_time = data.datas.TS_start;
      var step_time = data.datas.TS_step;
      // Format data for dygraph
      var formated_labels = ['Date'];
      var formated_datas = [];
      var first_line = true;
      for (var serie in data.datas.DATAS){
        formated_labels.push(serie)
        // Gen timestamp
        for (var i = 0; i < data.datas.DATAS[serie].length; i = i + 1) {
          // init data line value (do it just one time)
          if (first_line == true) {
            formated_datas[i] = [ new Date( (start_time + step_time * i) * 1000), data.datas.DATAS[serie][i]];
          } else {
            formated_datas[i].push(data.datas.DATAS[serie][i])
          }
        }
        // Second serie stop init formated_datas
        first_line = false;
      }

      // Make series
      var source_name = formated_labels[1];
      // Stacked or not
      var is_stacked = false;
      $.each(data.infos.Infos, function(k, v) {
        if ( v.draw !== undefined ) {
          if ( v.draw.indexOf('STACK') != -1 ) is_stacked = true;
        }
      });
      // Make series
      var series = {};
      $.each(data.infos.Infos, function(source, v) {
        series[source] = {};
        if ( v.draw !== undefined ) {
          if ( v.draw.indexOf("AREA") != -1 ) { 
              series[source].fillGraph = true;
          }
        }
      });
      var g = new Dygraph(
        $(into)[0],
        formated_datas,
        { labels: formated_labels,
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
    $.getJSON(url + '&res=' + res, function (data) {
      // Compute width
      var graph_div = $(into);
      var graph_container = graph_div.find('.graph-container');
      var label_container = graph_div.find('.label-container');
      var width = graph_container.css('width').replace('px', '');
        // heigth = graph_container.css('height').replace('px', '') / 2 - 50;

      var start_time = data.datas.TS_start;
      var step_time = data.datas.TS_step;
      // Format data for dygraph
      var formated_labels = ['Date'];
      var formated_datas = [];
      var first_line = true;
      for (var serie in data.datas.DATAS){
        formated_labels.push(serie)
        // Gen timestamp
        for (var i = 0; i < data.datas.DATAS[serie].length; i = i + 1) {
          // init data line value (do it just one time)
          if (first_line == true) {
            formated_datas[i] = [ new Date( (start_time + step_time * i) * 1000), data.datas.DATAS[serie][i]];
          } else {
            formated_datas[i].push(data.datas.DATAS[serie][i])
          }
        }
        // Second serie stop init formated_datas
        first_line = false;
      }

      // Stacked or not
      var is_stacked = false;
      $.each(data.infos.Infos, function(k, v) {
        if ( v.draw !== undefined ) {
          if ( v.draw.indexOf('STACK') != -1 ) is_stacked = true;
        }
      });
      // Make series
      var series = {};
      $.each(data.infos.Infos, function(source, v) {
        series[source] = {};
        if ( v.draw !== undefined ) {
          if ( v.draw.indexOf("AREA") != -1 ) { 
              series[source].fillGraph = true;
          }
        }
      });
      series.warning = {
        fillGraph: false,
        strokeWidth: 1.0,
        highlightCircleSize: 0.0
      };
      series.critical = {
        fillGraph: false,
        strokeWidth: 1.0,
        highlightCircleSize: 0.0
      };

      var g = new Dygraph(
        graph_container[0],
        formated_datas,
        {
          title: data.name,
          series: series,
          //height: 220,
          width: width,
          legend: 'always',
          //fillGraph: true,
          pixelsPerLabel: 60,
          gridLineWidth: 0.1,
          strokeWidth: 1.5,
          colors: data.colors,
          showRangeSelector: true,
          highlightCircleSize: 4.0,
          stackedGraph: is_stacked,
          labels: formated_labels,
          labelsDiv: label_container[0],
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
      return g;
    });
  };

  // UPDATE GRAPH
  numeter.update_graph = function (graph, res) {
    $.getJSON(graph.url + '&res=' + res, function (data) {

      var start_time = data.datas.TS_start;
      var step_time = data.datas.TS_step;
      // Format data for dygraph
      var formated_labels = ['Date'];
      var formated_datas = [];
      var first_line = true;
      for (var serie in data.datas.DATAS){
        formated_labels.push(serie)
        // Gen timestamp
        for (var i = 0; i < data.datas.DATAS[serie].length; i = i + 1) {
          // init data line value (do it just one time)
          if (first_line == true) {
            formated_datas[i] = [ new Date( (start_time + step_time * i) * 1000), data.datas.DATAS[serie][i]];
          } else {
            formated_datas[i].push(data.datas.DATAS[serie][i])
          }
        }
        // Second serie stop init formated_datas
        first_line = false;
      }

      graph.updateOptions({
        file: formated_datas,
        labels: formated_labels,
        colors: data.colors
      });
    });
  };

}(window, document, jQuery));
