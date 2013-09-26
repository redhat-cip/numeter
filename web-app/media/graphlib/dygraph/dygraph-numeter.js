//// SET GRAPH
var preview_request = null;
var requests = [];
var graphs =[];

// GET SIMPLE GRAPH
var Get_Simple_Graph = function(url, into_id) {
  preview_request = $.getJSON(url, function(data) {
    for (i in data['datas']){
      data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
    }
    g = new Dygraph(document.getElementById(into_id), data['datas'], {
      labels: data['labels'],
      colors: data['colors'],
      pixelsPerLabel: 60,
      gridLineWidth: 0.1,
      labelsKMG2: true,
      height: 150,
    });
  });
}
// GET ADVANCED GRAPH
var Get_Graph = function(url, into) {
  $.getJSON(url+'?res='+res, function(data) {

    // Compute width
    var width = $('.collapse').css('width').replace('px','') / 2 - 50
    // Make date
    for (var i in data['datas']) {
      data['datas'][i][0] = new Date(data['datas'][i][0] * 1000);
    }

    g = new Dygraph(document.getElementById(into), data['datas'], {
      title: data['name'],
      height: 250,
      width: width,
      legend: 'always',
      fillGraph: true,
      pixelsPerLabel: 60,
      gridLineWidth: 0.1,
      strokeWidth: 1.5,
      colors: data['colors'],
      showRangeSelector: true,
      highlightCircleSize: 4.0,
      labels: data['labels'],
      labelsKMG2: true,
      labelsSeparateLines: true,
      labelsDivWidth: 300,
      labelsDivStyles: {
        backgroundColor: 'rgba(200, 200, 200, 0.20)',
        borderRadius: '10px',
        padding: '4px',
      },
      axes: {
        y: {
          axisLabelWidth: 30000,
        }
      },
      series: {
        warning: {
          fillGraph: false,
          strokeWidth: 1.0,
          highlightCircleSize: 0.0,
        },
        critical: {
          fillGraph: false,
          strokeWidth: 1.0,
          highlightCircleSize: 0.0,
        },
      }
    });
    g.url = url;
    graphs.push(g);
    // MAKE ANNOTATION
    // var annotations = []
    // $.each( data['events'], function(i,v) {
    //   annotations.push({
    //     series: data['labels'][1],
    //     x: v['date'] * 1000,
    //     attachAtBottom: true,
    //     shortText: v['short_text'],
    //     text: v['comment']
    //   })
    // });
    // g.ready(function() {
    //   g.setAnnotations(annotations);
    // })
  });
}

// UPDATE GRAPH
var Update_Graph = function(graph) {
  $.getJSON(graph.url+'?res='+res, function(data) {
    for (j in data['datas']) {
      data['datas'][j][0] = new Date(data['datas'][j][0] * 1000);
    }
    graph.updateOptions({
      file: data['datas'],
      labels: data['labels'],
      colors: data['colors'],
    });
  });
}
