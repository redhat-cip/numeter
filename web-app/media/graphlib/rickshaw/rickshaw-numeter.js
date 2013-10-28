/*global Dygraph, window, document, jQuery, Rickshaw*/
(function (window, document, $, Rickshaw, undef) {
  'use strict';
  //// SET GRAPH
  var numeter, opacity, renderer;
  numeter = window.numeter = window.numeter || {};
  numeter.preview_request = null;

  renderer = {
    "LINE2": "line",
    "AREASTACK": "stack",
    "STACK": "stack",
    "AREA": "area"
  };

  opacity = 0.65;

  function parseData(rawData) {
    var palette, elt, color, series, infos, datas;
    series = [];
    palette = [
      [66, 61, 79],
      [74, 104, 96],
      [132, 143, 57],
      [162, 183, 60],
      [221, 203, 83],
      [197, 163, 47],
      [125, 88, 54],
      [150, 59, 32],
      [124, 38, 38],
      [73, 29, 55],
      [47, 37, 74]
    ];

    infos = rawData.infos;
    for (elt in infos) {
      if (infos.hasOwnProperty(elt)) {
        color = palette.shift() ||
          [
            Math.floor(Math.random()*255),
            Math.floor(Math.random()*255),
            Math.floor(Math.random()*255)
          ];
        series.push({
          name: infos[elt].label,
          renderer: renderer[infos[elt].draw] || "line",
          data: [],
          color: 'rgba(' + color.join() + ', ' + opacity + ')'
        });
      }
    }
    datas = series.map(function(elt){
      return elt.data;
    });
    fillDatas(rawData.datas, datas);

    return {series: series, datas: datas};
  }

  function fillDatas(rawDatas, datas) {
    var data, date, i, length, value;
    length = datas.length;

    for (i = 0; i < length; i = i + 1){
      datas[i].length = 0;
    }

    while ((data = rawDatas.shift()) !== undef) {
      date = null;
      i = 0;

      while ((value = data.shift()) !== undef) {
        if (!date) {
          date = value;
        } else {
          datas[i].push({
            x: date,
            y: value
          });
          i = i + 1;
        }
      }
    }
    return datas;
  }

  function createRickshaw(into, series) {
    var minimap, minimapC, legend, legendC, chart, chartC, yaxis, yaxisC,
      hoverDetail, shelving, xaxis, ticksTreatment, chart_display,
      chart_minimap, width, height;

    into = $(document.getElementById(into).parentNode);
    into.addClass('graph');
    into.empty();

    legendC = document.createElement('div');
    legendC.className = 'legend_container';
    legendC.style.overflow = "auto";

    chartC = document.createElement('div');
    chartC.className = 'chart_container';

    minimapC = document.createElement('div');
    minimapC.className = 'minimap_container';

    yaxisC = document.createElement('div');
    yaxisC.className = 'y_axis_container';

    chart_display = document.createElement('div');
    chart_display.className = 'chart_display';


    chart_minimap = document.createElement('div');
    chart_minimap.className = 'chart_minimap';

    chart_minimap.appendChild(chartC);
    chart_minimap.appendChild(minimapC);

    chart_display.appendChild(yaxisC);
    chart_display.appendChild(chart_minimap);
    into.append(legendC, chart_display);

    width = into.width() - $(legendC).width();
    height = into.height();

    chart_display.style.width = width + "px";
    chart_display.style.height = height + "px";

    width = width - $(yaxisC).width();
    //handle the bottom margin
    height = height - 10;

    chart = new Rickshaw.Graph({
      element: chartC,
      width: width,
      height: height,
      renderer: 'multi',
      stroke: true,
      preserve: true,
      series: series
    });

    chart.renderer.unstack = true;
    chart.render();

    hoverDetail = new Rickshaw.Graph.HoverDetail({
      graph: chart,
      xFormatter: function (x) {
        return new Date(x * 1000).toLocaleString();
      },
      formatter: function (series, x, y, formattedX, formattedY) {
        return [series.name, ':&nbsp;', formattedY, '<br/>', formattedX].join('');
      }
    });

    legend = new Rickshaw.Graph.Legend({
      graph: chart,
      element: legendC

    });

    shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
      graph: chart,
      legend: legend
    });

    ticksTreatment = 'glow';

    xaxis = new Rickshaw.Graph.Axis.Time({
      graph: chart,
      ticksTreatment: ticksTreatment,
      timeFixture: new Rickshaw.Fixtures.Time()
    });

    xaxis.render();

    yaxis = new Rickshaw.Graph.Axis.Y({
      graph: chart,
      orientation: "left",
      tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
      ticksTreatment: ticksTreatment,
      element: yaxisC
    });

    yaxis.render();

    return chart;
  }


  // GET SIMPLE GRAPH
  numeter.get_simple_graph = function (url, into_id) {
    numeter.preview_request = $.getJSON(url, function (data) {
      var element, chart, xaxis, yaxis;
      element = document.getElementById(into_id);
      chart = new Rickshaw.Graph({
        element: element,
        width: parseInt(window.getComputedStyle(element).width),
        height: parseInt(window.getComputedStyle(element).height) - 15,
        renderer: 'multi',
        stroke: true,
        preserve: true,
        series: parseData(data).series
      });
      chart.renderer.unstack = true;
      element.removeChild(element.childNodes[0]);
      chart.render();

      xaxis = new Rickshaw.Graph.Axis.Time({
        graph: chart,
        ticksTreatment: 'glow',
        timeFixture: new Rickshaw.Fixtures.Time()
      });

      xaxis.render();

      var yaxis = new Rickshaw.Graph.Axis.Y( {
        graph: chart,
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
        ticksTreatment: 'glow'
      });

      yaxis.render();
    });
  };

  // GET ADVANCED GRAPH
  numeter.get_graph = function (url, into, res) {
    $.getJSON(url + '?res=' + res, function (data) {
      var g, series, result;
      result = parseData(data);
      g = createRickshaw(into, result.series);
      g.url = url;
      g.datas = result.datas;
      numeter.graphs.push(g);
    });
  };

  // UPDATE GRAPH
  numeter.update_graph = function (graph, res) {
    $.getJSON(graph.url + '?res=' + res, function (rawData) {
      fillDatas(rawData.datas, graph.datas);
      graph.update();
    });
  };

}(window, document, jQuery, Rickshaw));
